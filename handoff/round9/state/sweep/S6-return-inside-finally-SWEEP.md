# Class sweep — "return inside finally"

Not in `tools/audit/bugclasses.json` (new class this round).

Round-9 finding: **D7-s3-51** (verified, low — `tests/nightly_ha.py:_async_check_a4` returns
from inside a `finally` block at line 1274, a PEP 765 hazard (SyntaxWarning on CPython 3.14).
The finder's harness `tools/audit/round9/D7/leads/nightly_finally_return.py` shows that of 2 arms
where the broken-price refresh raises a `BaseException` the inner `except Exception` does not
catch and the recovery refresh also raises, `_async_check_a4` returns normally in both — the
in-flight exception is discarded, `swallowed=2 of 2`).

## Enumerator

This box's default `python3` is 3.11.15 (PEP 765's `SyntaxWarning` needs 3.14+, the finder's
`venv314`, not present in this cloud container), so
`tools/audit/round9/D14/sweep/return-inside-finally/enumerate.py` widens the seam rule with an
AST walk instead: every `Try.finalbody` across `tests/*.py`,
`custom_components/heatpump_optimizer/*.py` and `tools/**/*.py`, checking for a `return`
(always escapes the finally, at any nesting depth) or a `break`/`continue` (a hazard only when no
loop already nested *inside* the same finally block catches it first).

Positive control: `nightly_ha.py:1274` reproduces D7-s3-51's own site exactly.
Null control: no other `return` inside any `finally` exists anywhere in the three scanned trees.
Perturbation: the finder's own `--fixed` arm (the `finally`'s `return` replaced by a flag checked
after the block) drops `swallowed` to 0, `syntax_warnings` to 0 — documented in the harness, not
re-run here (needs CPython 3.14 for the warning count; the swallowed-exception count is
Python-version-independent and was reproduced by this sweep's own re-derivation of the mechanism).

## Disposition

| seam | disposition | note |
|---|---|---|
| `tests/nightly_ha.py:1274` (`return` in `finally`) | **instance** | D7-s3-51 itself — a `return` always escapes the `finally`, discarding any in-flight exception from the `try`. |
| `tests/gate_lock.py:433` (`break` in a `for` loop nested inside `run_group`'s `finally`) | **not applicable** | The `break` exits the retry `for` loop that is itself entirely inside the `finally` block — it does not escape the `finally` or discard the outer `try`'s exception (`proc.wait()`'s return value is what the outer `try` returns; the `finally`'s signal/reap loop runs to completion or breaks out of itself only). |
| `tests/gate_lock.py:435` (`continue` in the same retry loop) | **not applicable** | Same reasoning — scoped to the inner loop, not a finally-level escape. |

## Count

N = 1 verified finding (D7-s3-51) + 0 additional sweep-confirmed instances (the two additional
AST hits are false positives of the naive "any break/continue in a finally" rule, correctly
excluded once loop-nesting is accounted for). **rca = false** (N=1 < 3, not a ledger class, not
barriered).

## Barrier proposal

Add a `tests/structure.py` check (or, once the box runs CPython 3.14+, `-W error::SyntaxWarning`
in the gate) that fails on any `return` directly in a `Try.finalbody`, and on a `break`/`continue`
in a `finally` not caught by a loop nested inside that same `finally`. Estimated gate cost: under
1s (pure AST walk, no imports, no HA boot).
