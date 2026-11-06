Partial delivery of R10-DISPATCH-AT-HANDOFF, repair after fix-review round 1 (blocked: the autofix hold's status filter was never executed under the self-test). Carry 3, Carry 6 (second-reviewer part), Carry 10, Carry 14, Carry 15 and Carry 16 in `bus.sh` and `review_packet.py`. The round-1 findings are answered here:
- Carry 3: `HPO_BUS_CHECKS` now replaces only the `gh api` call and the stub prints check-run JSON (name, status), so the `select(.status != "completed")` filter runs. Arms added: all autofix completed dispatches, a red completed job dispatches, in-progress holds (rc 3), queued closures-autofix holds, no autofix job dispatches (null).
- Carry 3, the read: moved into `autofix_inflight` — paginated, up to 4 tries decided by `gh_read.py --classify`, stderr kept; a failed read prints `bus: the check-runs of <sha> could not be read, so the autofix hold was NOT checked ...` with the gh line, where it was silent before. It proceeds (the 2026-10-24 ruling: dispatch never waits for CI).
- Carry 16: arm (b) added: a second review commit of the same tree, confirmed after a refused post, leaves `verdict/<pr>` at the first signed commit and posts there.
- Carry 15: an empty pid file is a live holder for a bounded settle (2 s) before takeover; the "two concurrent confirms produce one verdict commit and one post" control is built; the live-holder wait and dead-holder takeover arms stay.

Not built here (each stays in the roster entry of R10-DISPATCH-AT-HANDOFF), as in round 1:
- Carry 1 and Carry 2 (dispatch at the handoff ref) wait on the owner's policy text for `fix-review.md` and `standing-dispatch.md`.
- Carry 4 (refuse on a carry_audit, figure_lint or moved-head red in the packet): the owner's 2026-10-24 ruling stands, dispatch never waits for CI.
- Carry 5 (brief lines in `cloud_dispatch.py`), the `review_carry.py` half of Carry 6, Carry 7 (hold on a pending required context; amends the 2026-10-24 ruling), Carry 8 (three rounds; already in `three_rounds`), Carry 9 (model routing).
- Carry 11, Carry 12 and Carry 13 (dependabot delivery row, dependabot body patch, pending-ci drafts).

## Head

5c85b09644e07c5817c62a6e225ffc45a121cc96

## Mutation proof

Mutants are in `dev/audit/harnesses/r10_seat_selftests_mutants.py`. Run with `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py bus-10 bus-11 bus-13 bus-14 bus-15 bus-16` on the branch at the commit before the last main merge: all six KILLED, `RESULT survivors=0`.
- bus-14 (`select(true)`, the reviewer's mutant): KILLED, 2 failed.
- bus-15 (a failed read returns 0 silently): KILLED, 1 failed.
- bus-16 (`mut:pidsettle` removed): KILLED, 1 failed.
- bus-13 (`mut:autofixhold` to `if false`): KILLED, 3 failed.
- bus-11 (`mut:confirmlock`): KILLED, 1 failed.
- bus-10 (`mut:sametree` removed), planted by hand: fails exactly arm (a) "a repeated push-verdict of one verdict appends nothing", its null control, and arm (b) "a confirm on a second review commit of the same tree leaves verdict/<pr> at the first signed commit" — 3 failed.

## Null control

Each arm is paired with its null in the self-test: no autofix job dispatches; a new-nonce verdict still appends; a dead holder's lock is taken over; an empty pid left past the settle is taken over; the unmutated file passes every mutant step first.

## Figures

- `bash tools/audit/seat/bus.sh --self-test`: instrument for the check count and failures; it printed 0 failed at the head named above.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py`: instrument for the kill and survivor counts.

## Red checks

none. The check-runs API read over every page of the previous PR head 520550cebe311fad3d4f529c5267561ffe7e227c (`gh api --paginate .../commits/<sha>/check-runs`) lists only success and skipped conclusions. The head named above has run no checks yet, so its own are not read here. A governance / instrument-self-tests run that cancels at its 30-minute job timeout is main-wide and cured by R10-PROCESS-SLIM #3245, not by this diff.

## Forward-carry

The unbuilt carries stay verbatim in the R10-DISPATCH-AT-HANDOFF entry of `dev/programme/rosters/wave-r10-groups.json`, which must not be closed on this merge. Built here: Carry 3, Carry 6 (second-reviewer half), Carry 10 (already in the tree), Carry 14, Carry 15, Carry 16. Carry: dismissed: built in this diff or already in the tree

## Friction

none
