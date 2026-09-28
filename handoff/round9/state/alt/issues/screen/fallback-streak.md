**Source:** the #1736 shape screen ([SCREEN-1736-SHAPES.md](https://github.com/tvofi/heatpump_optimizer/blob/handoff/audit-r9-alt/handoff/round9/state/alt/SCREEN-1736-SHAPES.md)). The probe seat confirmed it with a null control. **The trigger is conditional:** the probe injected a failure specific to one entry's job, and no real configuration that produces one was found. Measured at origin/main `3490cb16`.

## What

The worker-fallback cap (#783) counts consecutive in-process fallbacks. Its state is shared across config entries: `_WORKER_FALLBACK_CAUSE` is a module global, and the streak lives in `hass.data[_WORKER_FALLBACK_STREAK]` (`coordinator.py:1037-1260`), one per hass. A successful process-worker solve in entry B runs `_clear_worker_fallback`, which resets entry A's streak and deletes A's repair issue.

**Probe** (`C1.py`): 8 intervals, with `WORKER_FALLBACK_CAP = 3`.

| arm | A's in-process (GIL) solves | A cycles refused at the cap | repair issue |
|---|---|---|---|
| probe: A fails, B succeeds, interleaved | **8** | **0** | created 8×, deleted 8× |
| null: A fails alone | 3 | 5 | created once |

If both entries fail, the shared count reaches the cap in 2 intervals instead of 4. That matches the documented per-hass design, so it is not a defect.

## Blast radius

- With two or more entries and a failure specific to one entry's job, the #783 cap never engages for the failing entry. It solves in-process and holds the GIL on every interval, unbounded.
- Its repair issue flaps every interval.
- **Introduced** by `546b4924` (2026-09-12). **First release v6.4.2.**

**Severity: low**, while no real per-entry failure is known.

## Evidence

`C1.py` and `C1.out` in [the evidence directory](https://github.com/tvofi/heatpump_optimizer/tree/handoff/audit-r9-alt/handoff/round9/state/alt/evidence/screen).

## Fix shape (R9-EG-B10)

- Key the streak and the cause by entry id. A per-entry failure then caps its own entry, and a failure affecting the whole install still caps each entry.
- Failing test first: the probe arm must refuse A at its cap.

## Disposition

Scheduled: **R9-EG-B10**, beside the in-flight refresh fix (`coordinator.py` solve lifecycle).
