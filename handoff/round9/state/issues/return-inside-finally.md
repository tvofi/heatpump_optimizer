# [R9-RETURN-INSIDE-FINALLY] return inside finally

**Class `return-inside-finally`.** return inside finally. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **low**.

N = 1 (1 judge-verified finding + 1 sweep-confirmed instance).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D7-s3-51 | `tests/nightly_ha.py` | low | nightly_ha._async_check_a4 returns inside finally: an in-flight CancelledError or KeyboardInterrupt is swallowed |
| sweep | `tests/nightly_ha.py:1274` | (unrated) | return in finally always escapes |

The sweep also checked, and excluded as not this class's fact (recorded so the count is not re-derived from scratch next round):

- `tests/gate_lock.py:433` — not applicable: break scoped to a for loop nested inside the finally, does not escape it
- `tests/gate_lock.py:435` — not applicable: continue scoped to the same nested loop

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D7-s3-51**: `python3 -W error::SyntaxWarning -c "import py_compile,glob; [py_compile.compile(f, doraise=True) for f in glob.glob('tests/*.py')]" (each failure is a seam); harness: tools/audit/round9/D7/leads/nightly_finally_return.py`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S6.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

AST check in tests/structure.py: fail on a return directly in Try.finalbody, or a break/continue in finally not caught by a loop nested inside that same finally.

## Fix

Fix: see round-9 fix plan.

