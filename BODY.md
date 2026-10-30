Adds `cancel_superseded.py sweep --repo R [--dry-run]` (triage P266, V180): cancels a PR branch's superseded runs from outside the run, so the queued-newer-run case (#2927, #2928: first push of open_pr.sh's two-push open) no longer holds runners. Reuses `candidates()`; one predicate, one owner. The CI-priority reader of V181/P267 is not on main; the sweep's own event filter keeps main-push runs and it does not wait on that group. Not carried: adoption by R10-ORCH-BEATD as a job.

## Head

6992e9bcb4119438e0175433d565870f68616dd9 (base cf4f6b7a6)

## Mutation proof

Mutant: `EVENTS` in tools/pr/cancel_superseded.py widened to include `"push"` (the event filter dropped). `python3 tools/pr/cancel_superseded.py --self-test` then reports 2 FAIL: "a merge_group or push run on this branch is never cancelled" and "sweep: a push run on main and a push run on a PR branch are never cancelled" (30 checks, 2 failed); restored, 30 checks, 0 failed.

## Null control

Only live-head runs cancels nothing (self-test "sweep null"); a bot-authored live head cancels nothing; an unreadable answer cancels nothing and exits 0; the unmodified tree has no `sweep` subcommand.

## Figures

- `python3 tools/pr/cancel_superseded.py --self-test` -> 30 checks, 0 failed at the head above.
- `python3 tests/structure.py` -> STRUCTURE RATCHET PASSED.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` -> MODE: SCOPED, runs tests/entities.py.

## Red checks

none

## Forward-carry

Carry 1 (V181 priority reader, owner's amendment): the reader and config file are not on main (P267/P268 group); the sweep's event filter already keeps main-push runs and the sweep calls the reader once it exists. Carry: R10-FLOW-WIP (dev/programme/rosters/wave-r10-groups.json)

## Friction

none
