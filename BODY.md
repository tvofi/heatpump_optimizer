Closes the R11-HOTFIX-SELFTEST-FLAKE-ARMS group (triage dev/programme/triage/r10-round-end.md#P782; root cause dev/audit/rca/R10-RCA-FAMILY-FLAKY-SELFTEST.md, state (c)). Two self-test arms asserted an ordering between concurrent processes with no barrier. Both are now ordered by explicit barriers. The third instance (carry 167, tests/entities.py redaction check) is already fixed on main by f38124f19c, which compares two clock-free payloads; nothing is changed there.

Alternatives that lost: retrying a red self-test once (refused in the RCA: hides a real intermittent defect, costs a job per red); an injected clock in beatd (the race is job ordering, not time). The one production line added to `bus.sh` confirm() touches `HPO_BUS_WAIT_MARK` only when set, so the arm can see the second confirm waiting on a live holder.

## Head

2bbfb7f3553b34732b515c92b2679fa2b64f23a2, measured 2026-11-15 13:21Z; origin/main tip at that time b3831ff64eca1936f0b618193ee86c3e337b51a9.

## Mutation proof

Predicate mutated in place, then restored: in `bus.sh` confirm() the lock acquisition `until mkdir "$lk" 2>/dev/null; do` replaced by `mkdir -p "$lk"; until true; do`. `bash tools/audit/seat/bus.sh --self-test` then reports FAIL for: "a confirm under a live holder's lock waits and moves nothing (P354)", "two concurrent confirms produce one verdict commit and one post (P354)", "a lock whose pid is not yet written is a live holder inside the settle (P354)" (3 failed). beatd: `python3 -I tools/audit/seat/beatd.py --self-test 9` reports "mutant m9_running_ignored turns (9) 'a running instance defers the restart to the next pass' red".

## Null control

Unmodified head: `bus.sh --self-test` 239 checks, 0 failed, including both existing P354 null controls (dead holder's lock taken over; empty pid past the settle taken over). `beatd.py --self-test 9`: 34 checks, 0 failed, including "null: with no restart taken the same job runs" and "null: behind only off the seat paths does not restart".

## Figures

- Instrument: 12 concurrent `python3 -I tools/audit/seat/beatd.py --self-test 9 --no-mutants` on one 4-core host with 6 CPU burners, counting runs with any FAIL line, `grep -l FAIL`. Base (origin/main beatd.py): 1 of 12 runs failed, the arm "a running instance defers the restart to the next pass". Head: 0 of 12. A single 12-run sample; the base rate is not established by it.
- Instrument: 8 concurrent `bus.sh --self-test` with 4 CPU burners, counting the P354 arm's result lines with `grep -h P354 | sort | uniq -c`. Head: the concurrent-confirm arm ok in 8 of 8. The base run of the same shape showed the arm ok too (0 failures of it in 8), so the base failure was not reproduced by this load; the arm's non-race is argued by construction (the second confirm now starts only after the first holds the lock inside the poster, and the gate opens only after the second is seen waiting), and its detection is shown by the mutation above.
- Unrelated reds seen under that 8x load, not owed here: base run, "a failed check-runs read is reported on a line, not swallowed (P344)" 4 times and "null control: no autofix job at all dispatches (P344)" once; head run, "a ref whose file main already carries under a moved path is SUPERSEDED" once. They are other timing-dependent arms of the same self-test under oversubscription.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED`, scope tests/doc_claims.py; `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` ALL 410 checks PASSED. `python3 tests/structure.py` RATCHET PASSED.

## Red checks

none

## Forward-carry

Carry 0 (tests/entities.py redaction check, wall-clock dependent) is discharged without a change in this diff: f38124f19c is on origin/main. Its control is in the tree: `PYTHONPATH=tests/hastub python3 tests/entities.py` reports ok for "the location is redacted whole, from data and from options, not coarsened", for "the rounded-coordinate search ignores a clock reading that contains one" (a poisoned clock reading that holds a rounded coordinate hits the whole-blob search and not the clock-free one) and for "a genuinely coarsened coordinate in the payload still fails the clock-free search". The check pins its own clocks, so the wall clock cannot reach it. Carry: dismissed: already repaired on main by f38124f19c

## Friction

none
