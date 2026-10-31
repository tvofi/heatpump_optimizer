The tick printed nothing for a merge verdict at the head of an unapproved PR (BLOCKED, REVIEW_REQUIRED), so #2962, #2976 and #2977 stood 11 h, 5 h and 5 h unflagged (triage P294, with the #2980 review finding 1). `prs()` now reads `reviewDecision`; `verdict_levels` adds `APPROVAL-OWED: #N <head8>` and the catch-all barrier `UNLEVELLED: #N <head8> <mergeStateStatus>/<reviewDecision>`; `owed_unactioned.py` carries both in FAMILY and key_of. The level reads the check state `one_pr` already judged (`_unsettled`: a pending, red, absent or unreadable check at the head), so no second API read; DIRTY, BEHIND, draft and UNKNOWN are named non-actionable in the docstring. Alternatives: naming the check in the line (rejected: the tick's gate lines already name it); UNKNOWN on two passes (rejected: needs state across passes; a named non-actionable state is simpler).

Root cause: no separate seat; the idle-PR class's seat is dev/audit/rca/R10-RCA-OWED-UNACTIONED.md, process state (c), and the catch-all is this class's barrier.

## Head

Measured at 5eeefa79eeabaa47103829aac5dfbc47009a2c32, `origin/main` 2fc0e95b2f3c merged in (prepr rerun at this head, rc 0, CI predict clean). Round 2: PR #3041 was blocked scope-incomplete (verdict/3041); this adds the REVIEW STALLED arm (triage P328, `dev/programme/triage/s6-batch90.md` on `handoff/triage-s8-batch90`, PR #3039 unmerged). Round-1 carry O1 (title claims stalled reviews, code added none) is answered by this diff.

## REVIEW STALLED (P328, round 2)

`verdict_levels` prints `REVIEW STALLED: #N <head8> <minutes>m` (flagged) for an open PR whose `(pr, head)` is in the bus dispatch record, which no approver verdict names, and whose `dispatch/reviewer-rev-<N>` tip is over `STALL_MINUTES` (90) old. Git only (`ls-remote`, `fetch`, `log -1 --format=%ct`), no REST and no run-log read (P280); an unreadable ref prints UNREADABLE, a missing ref is age 0. `owed_unactioned.py` carries it in FAMILY and keys it `#N` on head8, the minutes outside the key because they grow each sweep. Both instrument docs updated. Alternative rejected: reading the RemoteTrigger run log (P280).

Self-test rows: 100 min, no verdict: prints the line; nulls: 30 min dispatch, verdict at the head, dispatch at an older head; unreadable ref. Mutants (restored after each): age test `age > STALL_MINUTES` to `True` fails "a dispatch tip 30 min old prints no REVIEW STALLED"; verdict-at-head test to `False` fails "a verdict at the head ... prints no REVIEW STALLED"; dropping the `(pr, head) in dispatched` term fails "a dispatch at an older head ..."; removing REVIEW STALLED from owed_unactioned FAMILY fails 3 checks. `orchestrator_tick` self-test 235 checks, 0 failed; `owed_unactioned` 46 checks, 0 failed.

## Mutation proof

Predicate mutants of `tools/audit/seat/orchestrator_tick.py`, each restored after: (1) `if ms == "BLOCKED" and rd == "REVIEW_REQUIRED":` to `if False:` fails "verdict levels: BLOCKED + REVIEW_REQUIRED + merge at the head: APPROVAL-OWED, flagged, and nothing else"; (2) the UNLEVELLED `else:` to `elif False:` fails "the catch-all: BLOCKED under APPROVED prints UNLEVELLED with the state"; (3) dropping the `_unsettled` term fails "null control: a required check pending or red prints neither level". Each run: `orchestrator_tick self-test: 230 checks, 1 failed`.

## Null control

Failing test first: the BLOCKED + REVIEW_REQUIRED row printed nothing at the base. Null rows pinned: stale-head verdict, DIRTY, BEHIND, UNKNOWN, draft, and a pending or red check print neither level; APPROVED + CLEAN prints MERGE-READY only. At the head: `PYTHONPATH=tests/hastub python3 tools/audit/seat/orchestrator_tick.py --self-test` prints `235 checks, 0 failed`; `python3 -I tools/audit/seat/owed_unactioned.py --self-test` prints `46 checks, 0 failed`.

## Figures

- Mode line: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` prints `MODE: SCOPED`, 0 scripts selected.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- `bash tools/pr/prepr.sh` run at this head (mutants step skipped: no file mutants reads).

## Red checks

none

## Forward-carry

none

## Friction

none
