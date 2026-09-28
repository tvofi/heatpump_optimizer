**Source:** the owed trigger-1 RCA for the v6.6.0 options-flow freeze in [RCA-BULK-3.md](https://github.com/tvofi/heatpump_optimizer/blob/handoff/audit-r9-alt/handoff/round9/state/alt/rca/RCA-BULK-3.md) §4. The freeze is tvofi's CRITICAL report on #201 of 2026-09-17. Measured at origin/main `3490cb16`.

## What

The owner reported that on v6.6.0, saving or exiting the options flow froze the whole Home Assistant instance. The dispatched seat produced #1107, now 404. It fixed a real defect that occurred alongside the freeze (19 of 20 untouched pages reloaded). The v6.6.1 notes say it was "not a confirmed fix … still being diagnosed".

Since then, nothing in the record mentions the freeze: 11 days and 24 releases (v6.6.0..v6.7.10) with its status unknown. The trigger-1 RCA was never delivered.

**Cause: not established.** Static reading at `3490cb16` leaves these hypotheses, none measured:
- Every menu-mode page save calls `async_update_entry`, and each reload's first-solve task parks an executor thread on the process-global `_PROCESS_LOCK`. Unload cancels the task but cannot free a parked thread.
- `_build_data_dict`, the entity teardown and rebuild, and the sysid fit (#1658, 43–228 ms) run on the loop.

The #1658 `sensor_advisor` loop work came after v6.6.0, so it cannot be the v6.6.0 cause. **Whether the freeze is live cannot be settled without a live HA instance.**

**Process state: (c).** nightly-ha A5/A9 (#587, #655) round-trips every options form inside real HA. Its only loop instrument is HA's blocking-I/O detector, which is blind to CPU stalls: `tests/nightly_ha.py` has no heartbeat or max-gap measurement.

## Fix shape (R9-F10.7): instrument first

- Add a loop-heartbeat arm to nightly-ha A5/A9: a 1 ms `call_later` probe recording the max gap.
- Drive it with a two-zone + DHW config across three scenarios: an untouched exit, a changed save, and N changed saves in a row in menu mode.
- On a stall, capture `py-spy dump`.
- Nightly only; 0 s on PRs.
- **In parallel, an owner action:** HA's Profiler on the owner's host (`profiler.set_asyncio_debug`, then `profiler.start` across a reproduction).
- **The barrier decision is deferred** until the instrument finds the stall. The class is P10 (provisional), which register v2 records as a non-round instance.

## Disposition

Scheduled: **R9-F10.7**, after R9-F10.6. The host reproduction is tvofi's, and can run at any time.
