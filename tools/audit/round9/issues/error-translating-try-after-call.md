# [R9-ERROR-TRANSLATING-TRY-AFTER-CALL] error-translating try opened after the call it should cover

**Class `error-translating-try-after-call`.** error-translating try opened after the call it should cover. The mechanism the sweep confirms across 1 instance: the shared fact above is decided, guarded, or read differently at each site below rather than by one canonical rule, so a fix at one site leaves its siblings unfixed.

Highest severity: **medium**.

N = 1 (1 judge-verified finding + 1 sweep-confirmed instance).

RCA: not triggered (N=1).

## Instances

File:line is at baseline `1936d5ca` (`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`).

| ref | file:line | severity | what |
|---|---|---|---|
| D1-s2-55 | `custom_components/heatpump_optimizer/coordinator.py` | medium | A solve worker that cannot start (Popen OSError) skips the in-process fallback: no plan, no fallback notice |
| sweep | `custom_components/heatpump_optimizer/coordinator.py:1095` | (unrated) | _ensure_worker() called one line before the try it should be covered by |

## Reproduction

Per-finding seam rule / enumerator (each re-anchors at the baseline above; run `PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s harness contract):

- **D1-s2-55**: `grep -n '_ensure_worker()\|raise ProcessWorkerUnavailable\|except ProcessWorkerUnavailable' custom_components/heatpump_optimizer/coordinator.py; harness: tools/audit/round9/D1/leads/worker_spawn.py`

## Evidence

- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@2f97b0a`, `CLASSES-DRAFT.json@bad458a`.
- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.
- Class sweep output: `S6.json`.
- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1).

## Barrier proposal

None at N=1; generic call-before-try lint would have high false-positive rate.

## Fix

Fix: see round-9 fix plan.

