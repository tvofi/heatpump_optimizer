# Class sweep — "error-translating try opened after the call it should cover"

Not in `tools/audit/bugclasses.json` (new class this round).

Round-9 finding: **D1-s2-55** (verified, medium — `_run_in_process` (`coordinator.py:1091`) calls
`worker = _ensure_worker()` at line 1095, one statement *before* the `try:` at line 1097 whose
`except Exception as err:` exists specifically to translate transport failures into
`ProcessWorkerUnavailable`, the exception `_await_optimize`'s fallback path (line 1217) is written
to catch. `_ensure_worker` calls `subprocess.Popen(...)` directly (`coordinator.py:1014`), which
can raise a bare `OSError` (spawn failure, `ENOMEM`, missing interpreter path); that exception is
outside the try, so it propagates unhandled instead of triggering the documented
"degrade to in-process solve rather than no plan" fallback).

## Enumerator

`tools/audit/round9/D14/sweep/error-translating-try-after-call/enumerate.sh`: greps every site of
the worker-spawn/error-translation seam (`_ensure_worker`, the three `raise
ProcessWorkerUnavailable` sites, and the one `except ProcessWorkerUnavailable`) to confirm the
call/try ordering is exactly this one seam, and that no sibling seam shares the same
call-then-try shape elsewhere in `coordinator.py`'s worker-management code (`_await_process`,
`_shutdown_process_pool`, `_await_optimize` all read cleanly — the risky call in each is already
inside its own try, or the function has no error-translating except clause of this kind).

Positive control: the grep output shows `_ensure_worker()` at line 1095, one line before the
`try:` (line 1097, not shown by grep but adjacent in the source) — reproduces D1-s2-55's exact
line numbers.
Null control: `_await_process` and `_shutdown_process_pool` (also worker-lifecycle functions)
have no matching seam — neither wraps a spawn/connect call in a translating try at all, so there
is nothing to check them against; they are not false negatives of this specific mechanism.
Perturbation: moving `worker = _ensure_worker()` inside the `try:` block (one-line edit) makes a
`Popen`-raised `OSError` land in the `except Exception as err:` handler and come out as
`ProcessWorkerUnavailable` — the fix D1-s2-55 calls for, and the probe below fails before it and
passes after.

## Disposition

| seam | disposition | probe | note |
|---|---|---|---|
| `coordinator.py:1095` `_ensure_worker()` call, one line before the `try:` at `:1097` | **instance** | Mock `subprocess.Popen` to raise `OSError("spawn failed")`; call `_run_in_process`; assert it raises `ProcessWorkerUnavailable`, not a bare `OSError`. Fails at baseline (bare `OSError` propagates), passes once `_ensure_worker()` moves inside the try. | D1-s2-55 itself. |

## Count

N = 1 verified finding (D1-s2-55) + 0 additional sweep-confirmed instances (no sibling seam found
in the worker-lifecycle code). **rca = false** (N=1 < 3, not a ledger class, not barriered).

## Barrier proposal

None proposed at N=1 — a generic "call before try" lint would have a high false-positive rate
(most calls before a try are not meant to be covered by it); this is a fixer-time correctness fix,
not a structural gate.
