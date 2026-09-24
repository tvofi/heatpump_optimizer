<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi** · [project thread](https://claude.ai/code/project/chan_01EL5jLi4rokGBbkaevYXSJV?thread=cmsg_01EL5jLi4rokGBbkaevYXSJV1xHGMrg5ojcimoqRZJVNJ6)_

Pump-duty arbiter (judge option O1, as tvofi chose it): the optimizer tells the pump which duty to serve on each plan step. It works over Tuya or Modbus entities.

**Before:** the plan's DHW-only steps never reached the pump. With both set-points fixed at 53 °C, a planned DHW step ran as space heating. If the integration had written DHW-only, the mode read-back would have set `space_blocked` for the whole next horizon (`pump_signals.py` `space_blocked`, `optimizer.py` power caps zeroed). Nothing would then have written Heating + DHW back.

**After:** a new option, `pump_duty_mode`, with the values off (the default), observe and control. In control it writes, per 15-min step:
- **Mode:** DHW only on hot-water-only steps, and Heating + DHW otherwise. It never writes heating only.
- **DHW set-point:** the configured hot water set-point, not a literal.
- **Space set-point:** the weather-curve supply for a flow entity, or the step's planned room temperature for an indoor entity.

**How:**
- **Transport.** Where the mode select offers no DHW-only option (GCHV Modbus register 44), the space set-point is lowered to the entity's own minimum on DHW steps instead. The configured entities decide the transport.
- **Ownership.** The arbiter's own mode is marked `PumpSignals.mode_owned`. An owned mode blocks nothing, so the lock-in is gone and the setpoint and legionella notices do not fire on it. Capability and the learners still read the observed mode.
- **Manual changes.** A differing reading taken more than 20 s after the arbiter's write counts as a manual change. The 20 s clears the fork's 8 s sent-value echo. On a manual change the arbiter stops writing, turns Optimizer active off and raises the `pump_manual_change` repair. Re-enabling clears it.
- **Rails.** A DHW-only lease lasts at most 90 min, or 30 min below −10 °C outdoors. The baseline is written on a stale plan, comfort, boost or off mode, sysid, or unload. A pump in a cooling mode is left alone.
- **Timing.** A one-minute tick, active only when the option is not off, acts at step boundaries. The ownership record is persisted.

The tuya_heat_pump fork is unchanged.

## Head

58e0ff5e21d3b16e952cb1ae0cdcb5a32f47d12c (merge base 26f15eb0cf256d49f3443e814b9da17288a6f9fc)

## Mutation proof

Run on the arbiter section of `tests/features.py`:

| Change | Checks that fail |
|---|---|
| drop `not self.mode_owned` from `space_blocked` | "the arbiter's own DHW-only write does not block space heat in the next solve" |
| `ECHO_GRACE_S = 0` | "a differing reading inside the fork's echo window is not a manual change" |
| never report a foreign change | "a change the arbiter did not make turns the optimizer off…" and "turning the optimizer back on clears the repair…" |
| drop the lease | the 90-min and 30-min lease checks |

The deterministic inventory generates 62 candidate sites in `pump_arbiter.py`:
- 56 are killed by `tests/features.py` and recorded under `killed_by`.
- 6 are void, log-only or cost-only, and recorded under `survivor_triage` as equivalent, each with its reason.

## Null control

The lock-in test's own null control: a DHW mode nobody here wrote still sets `space_blocked`. At the merge base, `PumpSignals` has no `mode_owned` field, so the lock-in check fails there.

## Figures

- `python3 tests/structure.py` passes. `coordinator_loc` and `max_class_loc` rise by 2, for the two call sites. tvofi approved the raise in writing on 2026-09-24T17:58Z; the approval is cited in the commit message.
- `tests/mutation_table.py` `unpinned_sites` (the inventory ratchet) now sits below its recorded value.

## Red checks

`tests/entities.py` fails 3 checks locally, all environmental on this shallow clone and not from this diff:
- two checks on the HANDOVER `updated-for` ancestry;
- the pr-template acceptance arm.

## Forward-carry

none

## Friction

- gate-scoping: cost: `tests/closures.json` changing forces `MODE: FULL`, so the scoped gate cannot scope a new production module. features, entities, config_flow_steps, doc_claims, validate, deployment_shape and structure were run instead.
- mutation ledger: unclear: stale `.pyc` files, keyed on mtime and size, make same-size mutants run the previous mutant. A local mutation driver needs `PYTHONDONTWRITEBYTECODE=1`.

## Approval

Budget raise: `coordinator_loc` and `max_class_loc` 9062 → 9064 (commit 03ffae8). tvofi accepted budget raises for this feature in the project thread on 2026-09-24T17:58Z ("Budget raises will be needed for this and that is accepted"). As a budget PR it needs tvofi's own approving review before merge. No policy file changes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01S4GLCb85BVfbVgPghW2dKf
