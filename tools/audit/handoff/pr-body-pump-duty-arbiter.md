<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi** · [project thread](https://claude.ai/code/project/chan_01EL5jLi4rokGBbkaevYXSJV?thread=cmsg_01EL5jLi4rokGBbkaevYXSJV1xHGMrg5ojcimoqRZJVNJ6)_

Pump-duty arbiter (judge option O1, as tvofi chose it): the optimizer tells the pump which duty to serve on each plan step. It works over Tuya or Modbus entities.

**Before:** the plan's DHW-only steps never reached the pump. With both set-points fixed at 53 °C, a planned DHW step ran as space heating. If the integration had written DHW-only, the mode read-back would have set `space_blocked` for the whole next horizon (`pump_signals.py` `space_blocked`, `optimizer.py` power caps zeroed). Nothing would then have written Heating + DHW back.

**After:** a new option, `pump_duty_mode`, with the values off (the default), observe and control. In control it writes, per 15-min step:
- **Mode:** DHW only on hot-water-only steps, heating only on space-only steps (tvofi's revision: the cheapest space hours need not keep the tank ready for its next DHW window), Heating + DHW when both are planned or while the integration holds the disinfection switch on, no write on idle steps (the mode on the pump served the duty that just finished, whose thermostat the plan satisfied; Heating + DHW would arm both). Baseline is Heating + DHW.
- **DHW set-point:** the configured hot water set-point, not a literal; on Modbus space-only steps, the gate below.
- **Space set-point:** the weather-curve supply for a flow entity, or the step's planned room temperature for an indoor entity.

**How:**
- **Transport.** GCHV Modbus register 44 offers Off / Cool + DHW / Heat + DHW only, so where the select lists no single-duty option the other duty's set-point is the gate: space set-point to the entity minimum (floor 25 °C) on DHW steps, DHW set-point to the entity minimum (floor 30 °C) on space steps. The configured entities decide the transport.
- **Ownership.** The arbiter's own mode, DHW-only or heating-only, is marked `PumpSignals.mode_owned`. An owned mode blocks nothing, so neither lock-in exists and the legionella mode-block notice does not fire on it. `setpoint_check`'s disinfection-floor notice skips the arbiter's own DHW gate (`pump_arbiter.dhw_gated`). Capability and the learners still read the observed mode.
- **Unreadable mode.** An unavailable mode select is no reading (`_observed` returns `None` for a state `pump_mode.resolve` does not recognise). Before this, an `unavailable` select read more than 20 s after a write was a manual change and switched the optimizer off; found by the surviving `if observed is None` mutant, pinned by "an unavailable mode select is no reading…".
- **Ignored write vs manual change.** Each write records the reading just before it. A differing reading more than 20 s after the write (the fork's 8 s sent-value echo) that never showed our value and still equals the pre-write value is an ignored write: `pump_write_ignored` warning repair, the slot retried after 5 min, optimizer stays on, the first landed write clears it once no retry is pending; leaving control (observe, off, Optimizer active off) drops pending retries and the warning. Anything else — a third value, or any change after our value was read back — is a manual change: stop, Optimizer active off, `pump_manual_change` repair. Limits (in the module docstring and `docs/configuration.md`): a person restoring exactly the pre-write value before our value was read back, or a device reverting inside one reading interval, reads as ignored; after a restart the pre-write readings are gone and any difference is manual.
- **Rails.** A DHW-only lease lasts at most 90 min, or 30 min below −10 °C outdoors, idle steps after it included. The baseline is written on a stale plan, comfort, boost or off mode, sysid, or unload. A pump in a cooling mode is left alone.
- **Observe ledger** (observe and control): per 15-min step, planned duty against measured power (running), mode (DHW only) and tank rise ≥ 0.5 °C over the step; verdict delivered / space-instead / dhw-instead / idle-instead / unknown (no power entity, no tank rise) / baseline. Last 96 steps and counts under `pump_duty.ledger` in the diagnostics; not persisted. No running-mode or valve register is read: the integration has no slot for Modbus registers 45 or 210.
- **Timing.** A one-minute tick, active only when the option is not off, acts at step boundaries. The ownership record is persisted.

The tuya_heat_pump fork is unchanged.

## Head

f2117c0d8f931a4254cbc1a505eed346c54ec387 (merge base 26f15eb0cf256d49f3443e814b9da17288a6f9fc)

## Mutation proof

Run on the arbiter section of `tests/features.py`:

| Change | Checks that fail |
|---|---|
| drop `not self.mode_owned` from `space_blocked` | "the arbiter's own DHW-only write does not block space heat in the next solve" |
| `ECHO_GRACE_S = 0` | "a differing reading inside the fork's echo window is not a manual change" |
| never report a foreign change | "a change the arbiter did not make turns the optimizer off…" and "turning the optimizer back on clears the repair…" |
| drop the lease | the 90-min and 30-min lease checks |
| space step never picks the heating-only option | "the space step at the next boundary writes heating only…", "the arbiter's own heating-only write does not block hot water…", the indoor set-point check |
| drop the disinfection upgrade | "a disinfection cycle held on turns a space-only step into Heating + DHW…" |
| idle writes the baseline mode | "an idle step writes no mode…", "the hot-water-only lease keeps counting across idle steps" |
| lease resets on idle | "the hot-water-only lease keeps counting across idle steps" |
| Modbus DHW gate writes the configured value | "…the hot-water set-point is the gate, at the entity's minimum", "the arbiter's own hot-water gate raises no disinfection-floor notice…" |
| every differing reading is manual (`if True:`) | "a write the pump never took is a warning…", "an ignored write is sent again after five minutes…" |
| never record a landed write | "a return to the old value after our write was seen to land is a manual change" |
| drop the retry wait | the two ignored-write checks |
| never clear the warning on landing | "an ignored write is sent again after five minutes, and the first one that lands clears the warning" |
| drop `dhw_gated` from `setpoint_check._dhw` | "the arbiter's own hot-water gate raises no disinfection-floor notice; a person's 40 does" |
| tank rise threshold 99 °C | "observe keeps a per-step ledger…" |
| no meter reads idle instead of unknown | "without a power meter or a tank rise the ledger says unknown…" |
| always running | "observe keeps a per-step ledger…" |

The revision mutants above were run on the arbiter section alone (the file's import prelude plus the section), each restored after its run; every one failed at least one check.

Inventory ledger: every `mutation_table.candidates()` site in `pump_arbiter.py` at the head was driven the same way (driver: apply the site's `new` line, run the section, restore; killed = non-zero exit). 82 killed, recorded under `killed_by`; 4 survivors triaged `equivalent` with reasons (`if result is None`, `_differs`' None guard, `foreign_change`'s trailing `return None`, `_STORE_VERSION`). Two first-drive survivors were real and are now killed: the `if observed is None` skip (the unavailable-select fix above) and the retry-pop `and` (test tightened); `TANK_RISE_C` and `LOG_STEPS` survived the first drive and are now pinned by the ledger checks. `setpoint_check.py`'s existing dispositions were re-keyed to their shifted lines, `old` pins unchanged. `completeness_problems` returns none and `unpinned_sites` is re-recorded down to what `unpinned_sites(budgets, inventory())` returns.

The deterministic inventory generates 62 candidate sites in `pump_arbiter.py`:
- 56 are killed by `tests/features.py` and recorded under `killed_by`.
- 6 are void, log-only or cost-only, and recorded under `survivor_triage` as equivalent, each with its reason.

## Null control

The lock-in test's own null control: a DHW mode nobody here wrote still sets `space_blocked`; a heating mode the arbiter did not write still sets `dhw_blocked`. At the merge base, `PumpSignals` has no `mode_owned` field, so the lock-in check fails there. The own-gate notice check carries its own: a DHW set-point of 40 nobody wrote raises `dhw_setpoint_below_disinfection`. The ignored-write checks are paired with the manual-change checks, which set a third value (`Heating`) instead of the pre-write one.

## Figures

- `python3 tests/structure.py` passes. `coordinator_loc` and `max_class_loc` rise by 2, for the two call sites (commit 03ffae8). tvofi approved the raise in writing on 2026-09-24T17:58Z; the approval is cited in the commit message. The revision commit moves no budget.
- `tests/mutation_table.py` `unpinned_sites` (the inventory ratchet) re-recorded down to the measured count at the head.
- Run at the head, each rc=0: `tests/features.py`, `config_flow_steps.py`, `doc_claims.py`, `deployment_shape.py`, `validate.py`, `guard_pins.py`, `plan_view.py`, `manual_plan.py`. `tests/finite_boundary.py` fails "every derived boundary is wired to a loader in the reach sweep" at the head and identically at 93d95c8 (before this revision), so not from this diff.

## Red checks

`tests/entities.py` fails 3 checks locally, all environmental on this shallow clone and not from this diff:
- two checks on the HANDOVER `updated-for` ancestry;
- the pr-template acceptance arm.

## Forward-carry

none

## Friction

- gate-scoping: cost: `tests/closures.json` changing forces `MODE: FULL` (re-measured at the revision head with `closure.py select`), so the scoped gate cannot scope a new production module. features, entities, config_flow_steps, doc_claims, validate, deployment_shape, guard_pins, finite_boundary, plan_view, manual_plan and structure were run instead.
- import cycle: a first cut imported `pump_arbiter` from `setpoint_check`; `tests/guard_pins.py` failed at import (`repairs` → `setpoint_check` → `pump_arbiter` → `repairs`). The own-gate predicate is now installed by `pump_arbiter` on `setpoint_check.dhw_gated`, so `setpoint_check` imports nothing new and no recorded closure changes.
- mutation ledger: unclear: stale `.pyc` files, keyed on mtime and size, make same-size mutants run the previous mutant. A local mutation driver needs `PYTHONDONTWRITEBYTECODE=1`.

## Approval

Budget raise: `coordinator_loc` and `max_class_loc` 9062 → 9064 (commit 03ffae8). tvofi accepted budget raises for this feature in the project thread on 2026-09-24T17:58Z ("Budget raises will be needed for this and that is accepted"). As a budget PR it needs tvofi's own approving review before merge. No policy file changes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01S4GLCb85BVfbVgPghW2dKf
