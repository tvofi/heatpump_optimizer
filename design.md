# Design note: R11-SEAM-actuation-release

Extends the architect note and ADR-004 (plan 819aa2e354b4). Code read at `origin/main` 8751943e17ef4d3ec699e7859ae829b4528d8ce7; `after` is empty, so no predecessor head exists. Findings read at register 0a7ea717c6d9 (`dev/audit/rounds/round11/D16/s3/findings/D16-s3-02.json`, its five siblings, `D7-s1-05.json`); `git diff --stat 92d38ecb640b 8751943e17ef` (their baseline) leaves `off_restore.py` and `pump_arbiter.py` untouched.

## 1. Owning seam

`custom_components/heatpump_optimizer/off_restore.py` owns the restore: who is armed, when it runs, the retry, the persisted record. Each writer module owns its entity's write and record and only registers and arms: `pump_arbiter.py` (supply switch, arbiter row), a new circulation module (both pumps), `freq_control.py` (frequency), `mixing_valve.py` (valve). `coordinator.py` only calls. `legionella.py` owns its notice (ADR-001). One owner per concern; none needs two.

## 2. Shape

**Registry.**
- `_armed_record` (`off_restore.py:126` "held.loaded = True"): the first read runs under a lock on the record and `loaded` is set after it lands (D1-s2-04).
- `register_consumer` gains a keyword: also restored on a stale plan. A second registration form takes a release function `(hass, entry, config, reason) -> bool` instead of a one-entity restorer, armed as a neutral entry; the stored document and store version do not change.
- `async_restore` restores in registration order, takes a keyword restricting it to stale-plan consumers, skips a key whose restore is in flight, and saves only when the armed set changed.
- A new cycle entry, called once per cycle with two booleans (Off; plan stale): Off restores every armed key, stale the stale-plan keys, else nothing. Nothing armed is a dictionary test, no I/O. It is D16-s3-04's retry (one attempt per armed key per cycle) and D16-s1-04's trigger.
- `async_forget` also names a neutral key still armed at removal.

**Consumers** (keys in prose; none is in the tree yet).

| entity | write site at base | restored to | armed | stale plan |
|---|---|---|---|---|
| supply switch | `pump_arbiter.py:1960` `switch_supply` | on | before an off write | yes |
| arbiter mode, tank set-point, silent, night | `pump_arbiter.py:2130` `release` | the baseline row, by release function | before a non-space slot write | no |
| frequency | `coordinator.py:10845` `_command_frequency` | reading before the first write | each write | yes |
| valve target | `coordinator.py:7724` `_command_valve_target` | reading before the first write | each write | yes |
| space circulation pump | `coordinator.py:4558` `_async_set_pump` | on | before an off write | yes |
| hot-water circulation pump | same | on | before an off write | no |

- `switch_supply` takes the entry and config and arms itself; callers `write_supply` and `early_cutoff.py:326` change. Its restore clears the tick's record through `release_supply`.
- One function builds the baseline row with the cycle flags cleared (`disinfecting` false, no `dhw_reason`), space set-point excluded; Off and unload both reach it through the registry (D16-s3-01, D16-s3-03). `release` no longer writes. `__init__.py:426` restores before `async_shutdown`, so the row stops depending on the order at `coordinator.py:6617` `async_release_switch`.
- The supply registers before the row: the arbiter writes nothing while the switch reads off (`_pump_off`).
- `_pump_commanded` and the body of `_async_set_pump` move to the new module, the record held per config entry there as `pump_arbiter.py` holds its state, so the restore callback needs no coordinator attribute. `_async_drive_pumps` hands values.
- The tail of the frequency and valve methods (arm, dedupe, send, record) moves beside the record: `FrequencyWatchdog` in `freq_control.py`, and an owner in `mixing_valve.py` taking `_valve_commanded_target` and `_valve_write_problem`. The coordinator keeps the target computation.
- `_apply_action` calls the cycle entry before its Off and stale returns. The let-go predicate, spelled at `coordinator.py:7799` and `coordinator.py:3477` (both "_plan_is_stale"), becomes one helper read by those two, the frequency and the valve.
- `legionella.py:710` `check_overdue` and `legionella.py:741` `check_mode_block` call one helper that formats both placeholders and calls `set_issue`, as `m7_prototypes.py` at 0a7ea717c6d9 spells `notice`.

```
async_set_mode -> async_mode_change -> async_restore(all): supply on, row, space, frequency, valve, pumps, curve
cycle -> cycle entry: Off -> async_restore(all)       retry; also a write that raced the mode change
                      stale -> async_restore(stale)   supply on, frequency, valve, space pump
unload -> async_restore(all) -> async_shutdown -> async_release_switch -> release (no write)
remove -> async_forget (no write)      a restore that lands -> owner callback empties its record
```

**Invariants.** (1) An armed key is restored within one cycle of the optimizer letting go, or retried each cycle. (2) After a restore the owner's record of the entity is empty, so the first write after On is not deduplicated against a value the entity no longer holds; `R11-SEAM-actuation-writes` reads this. (3) No arbiter lock is awaited inside a restore and the registry holds no lock across a consumer's write: the arbiter arms under its own lock (`pump_arbiter.py:1732`). (4) In Off only the registry writes. (5) Entities, services and payload keys unchanged; `last_restore` gains a stale-plan reason.

## 3. Alternatives

- **Retry from the arbiter's Off pass** (D16-s3-04's perturbation): it runs under the arbiter lock while the row's release writes arbiter slots, against invariant 3, and `apply` returns at `pump_arbiter.py:1856` when the duty mode is off, so a curve-only install gets no retry.
- **A restorer per arbiter slot**: `Restorer` carries one entity and a float; the mode is a select option and the slot routing lives at `pump_arbiter.py:1610`, so the registry would hold a second copy of it.
- **Arming inside the two coordinator methods**: each gains an armed-entry read, a record reset and an arm, more statements than the circulation move removes.
- **The prototype's owner on a coordinator attribute** (`prototypes.py --only circ`, 819aa2e354b4): an entry-keyed restore cannot reach it, leaving a class that only holds the dictionary, which ADR-004 refuses.

## 4. Sibling sites

`python3 tools/audit/enumerate.py d16-writes | grep '^write'`: eight sites. Covered: `_command_frequency`, `_async_set_pump`, `switch_supply`, `pump_arbiter.py:1610`. Already registered: two in `heat_curve.py`. `inputs.py:729` is the sender under the valve and the space set-point. Out of scope: `coordinator.py:3438`, the disinfection switch, whose owner in `disinfection.py` keeps its own record and `release_blind`; no finding here measures it.
`grep -nE '\.loaded = True|_loaded = True' custom_components/heatpump_optimizer/*.py`: four. `off_restore.py:126` fixed; `pump_arbiter.py:2204` safe under its lock; `coordinator.py:9772` and `frontend.py:112` are other seams' records, unmeasured.

## 5. Evidence, by file

- **Failing tests first, `tests/features.py`.** Re-pin `tests/features.py:65074` "nothing else" to `dev/governance/dimensions/D16.md:48` "each written entity returned to its baseline once"; its null control (duty observe) stays. New checks with their null controls: four entities restored on Off and unload (null: commands equal to baseline); stale plan after an idle step switches the supply on (null: switch on at the last fresh step); a failed restore lands on a later Off cycle (null: no failure, no later write); concurrent first reads keep the restore and the stored baseline (null: serial); unload under a held disinfection writes the configured tank set-point (null: no hold); a valve write after Off then On is sent (null: no Off between).
- **Finder harnesses, both ends, at 0a7ea717c6d9**: `dev/audit/rounds/round11/D16/s3/m6_restore.py` (every `unrestored_` line 0, `null_` lines unchanged), `dev/audit/rounds/round11/D16/s1/cells.py --no-gates` (`baseline_switch_off` 0), `dev/audit/rounds/round11/D16/s3/m5_holds.py` (both `writes_again` lines 1), `dev/audit/rounds/round11/D1/s2/off_restore_race.py` (0; `--serial` 0), `dev/audit/rounds/round11/D7/s1/m7_prototypes.py --score --only notice`.
- **Score**: `tools/audit/archscore/` before and after. **Goldens**: no solver path changes; both claim files byte-identical.
- **Mutation targets**: `off_restore.py`: the lock and placement of `loaded`, both branches of the cycle entry, the in-flight skip, save-on-change, registration order. Circulation module: record-after-success, the let-go gate, both restorers. `pump_arbiter.py`: the cleared flags, the arm before an off write. `legionella.py`: the helper's raise-or-clear test.

## 6. Hot files, position, decisions

Hot: `off_restore.py`, `pump_arbiter.py`, `coordinator.py`, `legionella.py`, the new module, `tests/features.py`, `tests/seam_map.json`, `tests/closures.json`. First on the actuation chain. `pump_arbiter.py` is shared with `R11-SEAM-kernel-step` with no edge: the second to merge re-runs `m6_restore.py`. Receives no carry; owes `R11-SEAM-actuation-writes` invariant 2 with its control, the valve check.

- decision: orchestrator. `freq_control.py`, `mixing_valve.py` and `early_cutoff.py` join the roster's four hot files (alternative 3 is why).
- decision: owner. Frequency, valve and the space circulation pump are let go on a stale plan because each command is cut from the stale action; D16-s1-04 measures only the supply switch and states the property for "every entity it switched". The hot-water pump keeps writing: `coordinator.py:4517` `vvc_should_run` reads the clock and configured windows, not the plan. Narrowing to the supply switch is one keyword per registration.
- The brief's banking condition (orchestrator, 2026-11-18) is `pending owner confirmation`; this shape registers a restoring owner either way.
- ADR-004 names itself the approved design; this note adds the shape, siblings and evidence it leaves open.

## Notes for the fixer

1. `m6_restore.py --perturb consumers` wraps `switch_supply` and `_async_set_pump` by name: perturbed arms at base, unperturbed at head. Carry: R11-SEAM-actuation-release (item 1)
2. The register's enumerators under `dev/audit/rounds/round11/D14/` are at neither 0a7ea717c6d9 nor 819aa2e354b4; find them on the sweep refs before reporting release cells. Carry: R11-SEAM-actuation-release (item 2)
3. `__init__.py:426` restores before the released latch is set; test a tick queued across the unload. Carry: R11-SEAM-actuation-release (item 3)
4. Text stating the old rule moves too: the comment at `pump_arbiter.py:1869`, both module docstrings, anything `tests/doc_claims.py` pins. Carry: R11-SEAM-actuation-release (item 4)
5. A pump just switched on may not take the row's writes in the same pass; the retry covers only a write that fails. Carry: R11-SEAM-actuation-release (item 5)
6. If a base-pinned grader refuses the new module's registration, split p1 (registration) from p2 (the move). Carry: R11-SEAM-actuation-release (item 6)
7. The 2026-11-15 ruling is in `dev/governance/dimensions/D16.md`, not in `dev/programme/RULINGS.md`. Carry: dismissed: record gap for the orchestrator (item 7)
