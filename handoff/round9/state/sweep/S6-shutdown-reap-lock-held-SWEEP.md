# Class sweep — "shutdown reap waits on the lock a solve holds"

Not in `tools/audit/bugclasses.json` (new class this round).

Round-9 finding: **D1-s2-05** (verified, medium — `_run_in_process` (`coordinator.py:1094`)
holds `_PROCESS_LOCK` for the entire pickle-dump/pickle-load exchange with the solve worker — a
potentially long-running solve. `_shutdown_process_pool` (`coordinator.py:1047`), registered on
`EVENT_HOMEASSISTANT_STOP`, acquires the same `_PROCESS_LOCK` first, before it can check whether
the worker needs reaping at all, so HA's shutdown handler blocks behind an in-flight solve instead
of reaping the worker promptly — defeating the function's own stated purpose, per its docstring,
of avoiding exactly this kind of stall).

## Enumerator

`tools/audit/round9/D14/sweep/shutdown-reap-lock-held/enumerate.sh` greps every
`threading.Lock()`/`threading.RLock()` definition and every `_PROCESS_LOCK` acquisition across
the package, to check whether any *other* module-level lock has the same shape (one long-held
critical section for a solve/IO exchange, another acquisition path meant to run promptly on
shutdown).

## Disposition

| seam | disposition | note |
|---|---|---|
| `coordinator.py:968` (`_PROCESS_LOCK` definition), `:1047` (`_shutdown_process_pool`'s acquisition), `:1094` (`_run_in_process`'s long-held acquisition) | **instance** | D1-s2-05 itself — the only lock in the package, and its only two acquisition sites are exactly this finding's two ends. |

No other `threading.Lock`/`RLock` exists anywhere in `custom_components/heatpump_optimizer/*.py`,
so there is no sibling seam to disposition.

## Count

N = 1 verified finding (D1-s2-05) + 0 additional sweep-confirmed instances (no second lock in the
package). **rca = false** (N=1 < 3, not a ledger class, not barriered).

## Barrier proposal

None proposed at N=1: the fix (narrow `_run_in_process`'s critical section, or have
`_shutdown_process_pool` signal-and-reap without waiting on the lock a solve holds) is local to
one pair of functions; not worth a permanent structural gate for the package's only lock.
