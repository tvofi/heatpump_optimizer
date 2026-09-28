**Source:** the #1736 shape screen ([SCREEN-1736-SHAPES.md](https://github.com/tvofi/heatpump_optimizer/blob/handoff/audit-r9-alt/handoff/round9/state/alt/SCREEN-1736-SHAPES.md)). The probe seat confirmed arm (b) with a null control, and arm (a) is that probe's own arm read against the `O2`-alone control. This is not a judged audit finding. Measured at origin/main `3490cb16`.

## What

`async_run_optimization` returns early when a solve is already in flight (`coordinator.py:4895-4897`). Its docstring (`:4882-4884`) calls that "the same outcome for whoever asked". The guard sets no follow-up flag, and nothing re-runs the solve once the in-flight one finishes. That holds only if the asker's inputs are the ones the in-flight solve snapshotted. For an input change made during the window, it is false.

**(a) The re-solve after an input change is dropped.** `async_apply_manual_plan` (`:7600-7610`) and `async_clear_manual_plan` both adopt the new override, then `async_request_refresh()`. If a solve is in flight, that refresh's solve returns at the guard. In the probe, no solve ever ran against the new override O2 ("solves ran against: ['O1']"). The pump kept following O1's plan until the next scheduled cycle, while the service response and the sensor already showed O2's slots as applied. The same path covers any input change that relies on "refresh now": options, modes and services that request a refresh.

**(b) Stale releases are written onto the new override.** `_record_manual_release` (`:7562-7572`) writes the finished solve's safety releases into whatever `self._manual_override` holds after the await. It does not check that this is the override `_manual_pins` (`:7546`) read before the await.

**Probe** (`C2.py`): the solve await is gated, and the override is swapped O1→O2 inside the window.

| arm | solves ran against | O1.released_space | O2.released_space | published plan kW at O2's ON steps |
|---|---|---|---|---|
| probe: swap to O2 during the solve | ['O1'] | 0 | **41** (all O1's) | 2.39, 0.0, 1.0, 3.04, 4.82 (O1's plan) |
| null 1: no swap | ['O1'] | 41 | 0 | the same (O1's plan) |
| null 2: O2 alone | ['O2'] | 0 | 28 (its own, from step 13) | 1.58, 1.0, 1.1, 3.28, 5.0 |

## Blast radius

- A manual plan applied or cleared while a solve runs is **not actuated** until the next scheduled cycle, which is up to one optimization interval (30 min by default).
- Meanwhile the service response, the manual-plan attributes and the card show it as applied, with O1's releases attributed to O2.
- The same "already in flight" early return also lets a concurrent cycle publish the away setback (H1, carried to R9-EG-B1 on #1736).
- **Introduced** by `364d9b41` (the manual plan, 2026-08-22). **First release v3.2.0.**

**Severity: medium.** A user command is silently deferred while its receipt says it was applied.

## Evidence

`C2.py`, `C2.out` and `rig.py` in [the evidence directory](https://github.com/tvofi/heatpump_optimizer/tree/handoff/audit-r9-alt/handoff/round9/state/alt/evidence/screen).

## Fix shape (R9-EG-B10)

- The guard records a pending re-run, which the in-flight solve's `finally` honours, coalesced to one re-run.
- `_record_manual_release` writes to the override the solve pinned against, compared by identity.
- Failing tests first: arm (a) must end with a solve against O2, and arm (b) must leave O2 with none of O1's releases.

## Disposition

Scheduled: **R9-EG-B10**, after R9-EG-B9, since both are in the cycle region, and before R9-EG-B1 (plan principle 3).
