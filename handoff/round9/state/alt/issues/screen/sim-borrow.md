**Source:** the #1736 shape screen ([SCREEN-1736-SHAPES.md](https://github.com/tvofi/heatpump_optimizer/blob/handoff/audit-r9-alt/handoff/round9/state/alt/SCREEN-1736-SHAPES.md)). A read-only screen seat found it, and a probe seat confirmed it with a null control. This is not a judged audit finding. Measured at origin/main `3490cb16`.

## What

Two background callers borrow the user what-if's rate limiter and result cache around a full shadow solve:

- `_maybe_run_fuse_advisor` (`coordinator.py:8082`, borrow at `:8137-8141`);
- `_maybe_refresh_price_tile` (`coordinator.py:10191`, borrow at `:10214-10224`).

Each saves `(_last_simulation, _simulation_cache)`, awaits `async_simulate`, and **restores both unconditionally** in `finally`. That is the #1517 envelope shape. `async_simulate` stamps `_last_simulation` before its await (`:10820`). Its 3.0 s limiter (`const.py:632`, check at `coordinator.py:10730-10736`) therefore also sees the borrow.

**Probe** (`S2.py`): a gated window, with one tile solve measured at 0.66 s on this box.

| arm | user what-if U1 (asks 22.0) | cache after the window |
|---|---|---|
| (a) U1 lands inside the tile/advisor window | **rate-limited**; answered with the previous 20.0 | 20.0 |
| (b) U1 finishes inside a window held over 3 s | 22.0 | **reverted to 20.0**, and the limiter stamp is reset to U0's |
| null: no overlap | 22.0 | 22.0 |

- **Arm (b):** a follow-up U2 issued 0.7–2.7 s after U1 then runs a full solve instead of being limited. The null arm limits it.
- **The fuse-advisor rows** show the same results.

## Blast radius

- The card's what-if and the `simulate_plan` service: a wrong or stale answer, a spurious `rate_limited`, or a lost result.
- The CPU the limiter exists to cap, when the restore resets it.
- The tile docstring (`coordinator.py:10195-10201`) claims this cannot happen.
- **Exposure:** the tiles are off by default, and the advisor needs a fuse configured and runs at most weekly.
- **Introduced** by `f2d7a502` (the advisor, 2026-08-25) and `2e0d3d96` (the tile). **First release v4.0.0.**

**Severity: low.**

## Class

This is the #1736 class (`N-shared-config`), with an unconditional-restore envelope exactly like #1517's.

## Evidence

`S2.py` and `S2.out` in [the evidence directory](https://github.com/tvofi/heatpump_optimizer/tree/handoff/audit-r9-alt/handoff/round9/state/alt/evidence/screen).

## Fix shape (rides R9-EG-B9)

- Give the tile and the advisor a solve entry that neither reads nor writes the user limiter and cache: a private shadow-solve helper, with `async_simulate` keeping the limiter for callers only.
- The borrow and its `finally` are deleted, not repaired.
- Failing test first: arms (a) and (b).

## Disposition

Scheduled: **R9-EG-B9**, beside the boost fix in the same class.
