# Class sweep: N-restore-race (round 11, PLAN phase D)

Mechanism (bugclasses.json, status `open`): a restore applies persisted state
after an await during which a writer changed the same state.

## Enumerator
`python3 dev/audit/rounds/round11/D14/restore_race_seams.py custom_components/heatpump_optimizer`
lists every async function awaiting `async_load`/`load_mapping` (26 seams).
`UNGUARDED` = a `loaded` flag set before the read lands, no enclosing `async with`;
`WRITES` = state assigned after the await with no in-function lock.

- Positive control: flags `off_restore._armed_record` (D1-s2-04) UNGUARDED.
- Null control: clean fixture (flag inside `async with lock`) -> UNGUARDED 0.
- Perturbation: one line `rec.loaded = True` before the read in a copy of
  `duty_switch._load` -> UNGUARDED 0 -> 1.

## Dispositions
| seam | disposition |
|---|---|
| off_restore._armed_record | **instance** (D1-s2-04; probe `D1/s2/off_restore_race.py`) |
| pump_arbiter._load | guarded: both callers (L1859, L1917) hold `held.lock` |
| away.restore_override, boost.restore | guarded: `spawn_restore_session` gate; writers await `boost.session_restored` (R10 L3 fix) |
| coordinator._async_load_{thermal_learning,ledger,accuracy,energy_totals,manual_plan,snapshots,price_model}, _stored_fuse_advisor, _async_store_documents | guarded: run in setup before platforms/services register; savers wait via `QuarantiningStore.async_wait_for_read` (reports-B4 control: disabling it raises clobbers 5 -> 7) |
| dhw_learning.async_load_profile / async_load_draws | guarded for production: B4 report, no path folds a draw before the first interval; draws saver outside the read wait noted as residue |
| duty_switch._load | guarded: `loaded` set only after the read lands |
| legionella.async_load, notifier.async_load, debugger.async_load / async_setup_debugger | guarded: loaded during setup before the listener that writes is attached |
| frontend._register_lovelace_resource | not applicable: HA resource collection, no persisted state of ours |
| store.load_mapping, store.async_load, off_restore.async_forget, notifier.async_setup_notifier | not applicable: primitives / no post-await state write |

Instances beyond the finding: 0. Proposed barrier: the enumerator as a
`tests/` lint over the package (UNGUARDED must be 0 after the D1-s2-04 fix, with
`pump_arbiter._load` allow-listed by caller lock), sub-second gate cost.
