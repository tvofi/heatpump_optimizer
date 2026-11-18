# Design: R11-SEAM-config (round 11, size L)

Architect note, extended (`dev/governance/roles/designer.md`). Plan of record
`plan/r11` at 819aa2e354b4e5baaf824b8568fd72bea8168a75: `PLAN.md` (S18, T18;
"Designs" row), no ADR. Code read at the dispatched base
8751943e17ef4d3ec699e7859ae829b4528d8ce7 (`origin/main`); the group has no
`after` edge, so no predecessor head. Resumed from the stopped checkpoint
`handoff-wip/design-R11-SEAM-config` (c50b91f9, no design written). No
production code on this ref.

## 1. What each finding reads at the base (finder's harness, run here)

| finding | harness (under `dev/audit/rounds/round11/`) | at 8751943e17 | null / perturb |
|---|---|---|---|
| D17-s1-02 | `D17/s1/h_computed.py` `computed_kept_value_lost` | 8 | null 0; `--perturb-merged` 0 |
| D10-s2-01 | `D10/s2/reconfig_shadow.py` `shadowed_options_saved` | 2; `prefill_shows_running_indoor` 0 | `shadowed_null` 0 |
| D10-s1-03 | `D10/s1/cfg_data_options.py` `continue_settings_in_data` | 41 | `finish_now` 0 |
| D17-s2-05 | `D17/s2/after_save_stray.py` `entries_with_after_save` | 2 | — |
| D17-s2-04 | `D17/s2/silent_prefill.py` `kept_schedule_cap_delta_kW` | 0.000; `offered_fraction_on_setup_page` 0 | `with_fraction_cap_delta_kW` -2.000 |
| D4-s2-01 | `D4/s2/flow_errors.py` `unfilled_placeholders_total` | 8 | control cells 0 |
| D6-s3-01 (merged) | `D6/s3/prefill_placeholders.py` `config_refusal_missing` | 2; `changed_vs_preview` 3 | `options_refusal_missing` 0 |

All seven are live. The three class enumerators the issue bodies name (N-entry-data-placement,
I4, N-dead-input) are in no ref fetched here; §5 enumerates by its own commands.

## 2. Owning seam

Config surface. **Owner of where a key is stored**: `entry_config.py`, which
already owns every (data, options) pair (`settings_of`, `with_settings`,
`factory_settings`, `undone_settings`). **Owner of the forms**: `config_flow.py`.
Callers only: `__init__.py` (the migration), `coordinator.py` and
`services.py` (writers, untouched: they already write options), `silent_mode.py`
(untouched, §4). `tests/seam_map.json` maps `__init__` to core and names no
other file here. One concern, one owner each; no split.

## 3. Shape

**A. One place per key (D10-s1-03, D10-s2-01, T18).**
- In `entry_config.py`, a placement function: given the effective mapping
  `{**data, **options}`, return (data, options) with data holding only the
  data-only keys, every other key in options. The data-only key set is an
  explicit frozenset beside it: the first-screen keys (`user`, `user_sensors`)
  that no options page edits. A test derives that difference from
  `_OPTION_FIELDS` and `_first_screen_schema` and fails when the frozenset
  differs, so the set has one home and a new option row moves its key.
- Writers through it: `_create_setup_entry` (`async_create_entry(data=,
  options=)`), `_async_save_reconfigure` and `async_step_reauth_confirm`
  (each merges its answers over the effective mapping, places, and writes
  both sides in one `async_update_entry`), and `undone_settings` /
  `factory_settings` return placed pairs, so the reset writer at
  `coordinator.py:1499` "data=settings[0]" stays as is.
  The options flow and the service/coordinator option writers already write
  options only and need no change.
- Reconfigure prefill (both `add_suggested_values_to_schema` calls) reads the
  effective mapping, not `entry.data`.
- **Migration**: a minor version, not a major one. A minor-version class attribute of 2 on
  `HeatPumpOptimizerConfigFlow` (`CONFIG_ENTRY_VERSION` stays 7);
  `async_migrate_entry` places any entry with `version < 7` or minor `< 2`
  and stamps both. Invariant: the effective mapping is equal before and after
  (placement only moves keys; on a key in both sides the options value, the
  one in force, is kept).

```
before: setup -> data{41 settings}; options page -> options; reconfigure/reauth -> data (shadowed)
        reader: {**data, **options}
after:  every writer -> placement(effective) -> data{data-only}, options{rest}
        reader unchanged: {**data, **options}
```

**T18 answered by the minor version.** Home Assistant loads an entry whose
minor version exceeds the integration's on the same major, and the previous
release's `async_migrate_entry` refuses only `version > 7`; that release reads
`{**data, **options}`, which the migration leaves equal. A downgrade therefore
loads with the same settings. Residual, for the release notes: a reconfigure
or reauth saved *under the downgraded release* writes data again and is
shadowed until the next save under this one. The notes state the step first
(PLAN risk row T7/T16/T18).

**B. Computed defaults over the saved configuration (D17-s1-02).**
`_omit_unstored_computed` evaluates `row.default.of` over
`{**current, **(submitted non-computed keys)}`. Both callers (options
`_save_or_menu`, setup `async_step_device_prefill`) get it.

**C. One pre-fill page (D4-s2-01, D6-s3-01, D17-s2-05).**
- One module-level page builder used by `_device_prefill_form` and
  `_prefill_form`: placeholders `{**_WINDOW_PLACEHOLDERS,
  **device_prefill.disclaimer(), **notes}`.
- The setup flow keeps the preview's `(keys, notes)` on `_device_prefill`, the
  shape of the options flow's `_prefill`, and its refusal passes `notes`.
- The field builder under `_prefill_schema` is split from `_options_schema`'s
  after-save append: the options page wraps it, the setup page does not, so
  the setup page posts no `after_save` (its navigation is always
  `finish_setup`). Its `config.step.device_prefill` after-save label goes.

**D. A kept night-mode schedule caps (D17-s2-04).** Both pre-fill pages pair
`CONF_SILENT_MODE_FRACTION` with `CONF_SILENT_MODE_WINDOWS` (one pairing
mapping beside `_prefill_schema`): the fraction field appears whenever the
window field does, suggested from the effective value. `_prefill_errors`
refuses a kept non-empty schedule whose effective fraction is `>= 1.0` with
a new error key on the fraction field (all language files, no placeholder).

## 4. Alternatives (lost on the code)

- **Data keeps the first screens, options flow writes those keys to data**
  (finder's D10-s2-01 scope): the four option writers in `services.py` and
  `coordinator.py` that write entity slots into options would each need the
  rule; placement-by-options-editable needs none of them changed.
- **Major version 8**: the previous release's migrate returns False on
  `version > 7`, so a downgrade stops loading; the minor bump buys the same
  migration hook with a loadable downgrade.
- **D17-s2-04 in `silent_mode` (schedule with no fraction caps at a default)**:
  changes the plan of every install that saved a schedule with 1.0 on the grid
  page, a behaviour no finding names (designer.md stop rule).
- **Normalising placement at every setup instead of versioning**: the brief
  requires a versioned migration, and an unconditional rewrite at setup cannot
  tell which side is fresher after a downgrade either.

## 5. Sibling sites (commands)

- Entry writers: `git grep -nE 'async_update_entry\(|async_create_entry\(' --
  custom_components/heatpump_optimizer` (14). Covered: `config_flow.py`
  create, reconfigure, reauth; the reset writer in `coordinator.py` via
  `entry_config`.
  Options-only writers (options flow, `coordinator.py` 4265/6585,
  `services.py` 880/945/1097, `debugger.py` 713) are correct under §3 A;
  `__init__.py` 226 is the migration; `repairs.py` 56 is a repair flow, no entry.
- `data=` writes: `git grep -nE '\bdata=' --
  custom_components/heatpump_optimizer/config_flow.py` (create 2935,
  reconfigure 2877, reauth 3300): all three covered.
- Pre-fill renders: `git grep -nE '_device_prefill_form\(|_prefill_form\('
  -- custom_components/heatpump_optimizer/config_flow.py` (7 calls): all go
  through the one builder.
- Computed defaults: `git grep -c '_Computed(' --
  custom_components/heatpump_optimizer/config_flow.py` (13; 12 rows per
  `h_computed.py`): one function serves all.
- Out of scope: the grid page's windows-with-1.0 (both fields shown there; no
  finding); the `tibber_info` placeholder (I4 sweep row 3, finding D10-s2-03,
  `R11-SEAM-product-text`); `const.py`'s two-zone "options cannot erase"
  comment becomes stale (§7).

## 6. Evidence plan, by file

- **Failing tests first** (`tests/config_flow_steps.py`): weekday changed,
  weekend kept on Comfort (and B=A null); reconfigure after an Entities save
  takes effect and prefills the running value (null: no options); setup
  `continue` walk stores 0 settings in data and the effective mapping is
  unchanged; setup pre-fill refusal carries every placeholder of its strings
  and the preview's notes; no `after_save` in a created entry; kept schedule
  with fraction 1.0 refused, with 0.6 stored. `tests/entities.py` beside the
  existing migration cases (15559-15579): a v7 minor-1 entry migrates with
  equal effective mapping; a minor-2 entry passes the previous release's
  `async_migrate_entry` (taken from the last tag) and reads the same mapping.
- **Finder's harnesses at both ends**: the seven rows of §1 read 0 (D17-s2-04:
  the refused save, or `kept_schedule_cap_delta_kW < 0` once the paired
  fraction is kept), each null unchanged.
- **Goldens**: none move; placement leaves the effective mapping equal, so no
  claim file is touched.
- **Mutation targets**: the data-only membership test in the placement
  function; the minor-version comparison in `async_migrate_entry`; the merged
  mapping in `_omit_unstored_computed`; `_WINDOW_PLACEHOLDERS` in the page
  builder; the `>= 1.0` refusal comparator.

## 7. Hot files, serial position, carries

`after: none`. Hot-file order (`PLAN.md`): `config_flow.py` after
plant-model; `const.py` after kernel-layering and kernel-step;
`translations/en.json` before product-text; `__init__.py` after inputs-guards.
Adds beyond the roster's files: `entry_config.py`, `strings.json` and the
other translation files (new error key, removed label): text before
`R11-SEAM-product-text`, which is after every behaviour group. Named at 0.0:
`literal_clone_copies` (the merged page builder may lower it; banked only on
review). Owes the release-notes step first (T18). Receives no carry.

### Notes for the fixer

- `async_create_entry(options=)` exists on `ConfigFlow` only; check the
  hastub supports it and the minor-version attribute, or extend the stub in the same PR. Carry: R11-SEAM-config (item stub-minor-version)
- `diagnostics.py` already redacts across both sides (`_private_values` over
  data and options), so moving the token into options exposes nothing; re-run
  its redaction test. Carry: R11-SEAM-config (item token-redaction)
- `const.py`'s two-zone comment ("options cannot erase them") is no longer
  true after §3 A; reword it to what the code does. Carry: R11-SEAM-config (item two-zone-comment)
- An undo record written before the migration restores settings into data;
  `undone_settings` placing its result is what covers it, test it. Carry: R11-SEAM-config (item undo-record-placement)
