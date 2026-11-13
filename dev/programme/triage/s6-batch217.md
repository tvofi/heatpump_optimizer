# Proposal triage, session s14, batch 217

Sources: triage queue line 334, one PROPOSAL line (orchestrator s14, 2026-11-11T21:47:52Z),
ruled as P657. Line numbers are at origin/main 61afd4f2db. Roster read at
handoff/audit-r10-roster 558aa0e518. The accepted part is a carry on an existing group, so the
open-PR cap does not bear on it.

## P657: the tick's RED-UNOWNED reads a carried merge verdict as no verdict

Verdict: ACCEPT the orchestrator_tick.py part as a carry on R10-TICK-RESIDUE-P3; REJECT the verdict_audit.py part (refuted: its merge arm does not compare the head).

Source: triage queue line 334.

Instances, verified at the refs:
- #3452: verdict/3452 (79e2d9dcba) reads `Fix review: merge e099eff6a5`; the PR head 586f8ebec5
  is a merge of origin/main whose first parent is e099eff6a5.
- #3428: verdict/3428 (eaa8684e75) reads `Fix review: merge 846f2dc07b`; the PR head c6b73e7a0a
  is a merge of origin/main whose first parent is 846f2dc07b.

Cause, measured in the code:
- tools/audit/seat/orchestrator_tick.py:253-256, `verdict_kind`, returns `merge` only when the
  verdict names exactly the head. The bucket classifier (:1013-1014) therefore never reads a
  merge verdict on a main remerge as `verdicted`. It falls through, and a PR with a red check
  and no seat on it prints `red ..., no verdict at head, no seat on it` (:1031-1032,
  `red-unowned`).
- The tick already owns the train's carry predicate: `_carries(verdict, head)` (:1067-1073)
  runs `app_approve.sh --carry` through ledger.app_approve_carries, and REVIEW OWED uses it.
  The bucket classifier does not.
- The verdict_audit.py half is refuted. Its merge arm (verdict_audit.py:64-66) does not
  compare the verdict sha with the head: it prints `UNHELD ... owed to the merge train` only
  when the PR is absent from the train log and nobody holds it. Both instances were in the
  train, so verdict_audit printed nothing for them, and it never prints "no verdict at head".
  The words come only from the tick. This is not a duplicate of verdict_audit's own state.

Duplicate check: no carry on R10-TICK-RESIDUE-P3, R10-TICK-RESIDUE-P2 or R10-GATE-DEFER-BARRIER
names the bucket classifier's carry read; R10-ORCH-DISPATCH-REG carry 12 (REVIEW OWED's carry
skip) is built and is a different line.

Accepted change (carry): when the latest verdict is `Fix review: merge <at>` and `at` is not the
head, the classifier asks `_carries(at, head)` before any owed arm; a carried head is
`verdicted`. A failed fetch carries nothing (the head stays as today). The `WAIT is not red`
half of the ask needs no separate read: a carried head returns before the red arm.

Basis: severity-exempt defect repair (a false owed line, two instances in one day, each an
orchestrator turn and a merge-seat read), reusing a predicate the tick already holds. On the
20% bar alone it would be REJECTed.
