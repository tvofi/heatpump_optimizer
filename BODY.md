The tick printed nothing for a merge verdict at the head of an unapproved PR (BLOCKED, REVIEW_REQUIRED), so #2962, #2976 and #2977 stood 11 h, 5 h and 5 h unflagged (triage P294, with the #2980 review finding 1). `prs()` now reads `reviewDecision`; `verdict_levels` adds `APPROVAL-OWED: #N <head8>` and the catch-all barrier `UNLEVELLED: #N <head8> <mergeStateStatus>/<reviewDecision>`; `owed_unactioned.py` carries both in FAMILY and key_of. The level reads the check state `one_pr` already judged (`_unsettled`: a pending, red, absent or unreadable check at the head), so no second API read; DIRTY, BEHIND, draft and UNKNOWN are named non-actionable in the docstring. Alternatives: naming the check in the line (rejected: the tick's gate lines already name it); UNKNOWN on two passes (rejected: needs state across passes; a named non-actionable state is simpler).

Root cause: no separate seat; the idle-PR class's seat is dev/audit/rca/R10-RCA-OWED-UNACTIONED.md, process state (c), and the catch-all is this class's barrier.

## Head

Measured at 76d7da184813eb18b2f82deae22425ea18978372, `origin/main` 0d33c9348b39 merged in (main unmoved since; prepr run once at this head).

## Mutation proof

Predicate mutants of `tools/audit/seat/orchestrator_tick.py`, each restored after: (1) `if ms == "BLOCKED" and rd == "REVIEW_REQUIRED":` to `if False:` fails "verdict levels: BLOCKED + REVIEW_REQUIRED + merge at the head: APPROVAL-OWED, flagged, and nothing else"; (2) the UNLEVELLED `else:` to `elif False:` fails "the catch-all: BLOCKED under APPROVED prints UNLEVELLED with the state"; (3) dropping the `_unsettled` term fails "null control: a required check pending or red prints neither level". Each run: `orchestrator_tick self-test: 230 checks, 1 failed`.

## Null control

Failing test first: the BLOCKED + REVIEW_REQUIRED row printed nothing at the base. Null rows pinned: stale-head verdict, DIRTY, BEHIND, UNKNOWN, draft, and a pending or red check print neither level; APPROVED + CLEAN prints MERGE-READY only. At the head: `PYTHONPATH=tests/hastub python3 tools/audit/seat/orchestrator_tick.py --self-test` prints `230 checks, 0 failed`; `python3 -I tools/audit/seat/owed_unactioned.py --self-test` prints `43 checks, 0 failed`.

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
