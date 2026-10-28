R10-FLOW-ROSTER-FREEZE close-out: what #2389 and the group's carries still required on main after arms (a) 07cbe6fe1, (b) 24b4399cf / 3d526a7f3 and #2779, and the two pieces this pull request lands. Refs #2389: the roster lists it under the group's `issues`, not `fixes`, so pr-contract leaves its disposition to the orchestrator once the group closes.

Requirement by requirement, measured at origin/main 07295d4ea:

- (a) relay freeze while a review is in flight: met by 07cbe6fe1 (`review_freeze` and the handoff arm in `tools/audit/seat/cloud_relay.sh`), pinned by its self-test's `HELD-REVIEW` checks and mutants cloud_relay-22..28.
- P-H, freeze on a merge verdict at the live head: met by 07cbe6fe1 (`HELD-VERDICT`), with the four null controls the triage asked for in the self-test.
- Hold-file grammar and its ROSTER-APPEND text: the grammar is met (`hold_list`, nine malformed variants in the self-test), and the ROSTER-APPEND text is already the group's fourth `carry` entry on main's roster. Nothing is owed.
- (b) carry_audit reads the round's roster ref: met by #2779 (c01d54b98), pinned by the `load_dests reads the round ref` self-test checks.
- P98 arm (b2), stale tree: **not met on main**. `load_dests` read the tree's roster even when HEAD lacked origin/main. This PR lands it.
- #2792 review, mutant R1 in `review_freeze` survives: **not met on main** (it survives, see Null control). This PR adds the self-test arm that kills it.
- Card 1, retiring the standing roster seat: the runner exists (`tools/audit/seat/roster_queue.py`, d17df53c5), but no beat or daemon job invokes it, and the card's acceptance needs a live job beside the seat for one cycle. That is a beat job in R10-ORCH-BEATD's files (`daemonize.py`, `tick_loop.sh`), not this group's. It is routed under Forward-carry, and `standing-roster.md` is left alone, since the card puts its edit in whichever group merges later.

Change:

- `tools/audit/carry_audit.py` `load_dests`: with no `--roster-ref`, when `git merge-base --is-ancestor origin/main HEAD` answers rc 1, the roster is read at origin/main through `roster_lib.show_roster`, printing `NOTE stale tree: <HEAD> lacks origin/main <sha>; roster read at origin/main`. A checkout containing origin/main keeps its tree. A clone without origin/main answers some other rc and also keeps its tree. The round-ref union from #2779 is unchanged. Self-test: a scratch repo built through `tests/throwaway_git.py` puts HEAD behind origin/main, and a carry to a group that exists only on main passes with the NOTE. A group on neither ref is still BAD (null control). A HEAD containing origin/main keeps the PR's own new group and prints no NOTE (null control).
- `tools/audit/seat/cloud_relay.sh` self-test: a verdict ref the listing names but the fetch cannot find, or a listed sha the fetched ref does not carry, is `UNREAD` and frozen. The same ref listed at its own sha, holding a verdict at an older head, freezes nothing (null control). No production line changes.
- Mutants: B2-ancestry and B2-always in `dev/audit/harnesses/r10_carry_parser_mutants.py`. cloud_relay-34, the #2792 R1 mutant, is a per-file id placed inside the freeze block of `dev/audit/harnesses/r10_seat_selftests_mutants.py`.
- `tools/audit/seat/INSTRUMENTS.md`: the freeze paragraph names `HELD-UNREAD`.

Alternatives: for (b2), reading carry files at origin/main as well was rejected because the carry names the roster only, and a wider read would change which issues count as owned on a pull request's own tree.

## Head

b9a66d28d0554c95c4e961684bc3b91ed1b1c719, measured against origin/main 07295d4ea1471048ee2a76a6776b5cd364dcf141.

## Mutation proof

- `python3 dev/audit/harnesses/r10_carry_parser_mutants.py B2-ancestry`: killed, failed=2: `FAIL a tree behind origin/main reads the roster there: a group only on main passes`, `FAIL ... and says so: NOTE stale tree names HEAD and origin/main`.
- `python3 dev/audit/harnesses/r10_carry_parser_mutants.py B2-always`: killed, failed=2: `FAIL a tree containing origin/main keeps its own roster: the PR's own new group passes`, `FAIL ... and prints no stale-tree NOTE (null control)`.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-34`: `KILLED rc=1 | cloud_relay self-test: 279 checks, 3 failed`.

## Null control

- Failing test first: the new carry_audit self-test arms on main's `load_dests` give `carry_audit self-test: 201 checks, 2 failed`, the two stale-tree checks. After the fix: `201 checks, 0 failed`.
- cloud_relay-34 on main's self-test, run from a detached worktree of origin/main with only the harness entry added: `SURVIVED rc=0 | cloud_relay self-test: 275 checks, 0 failed`. That is the #2792 survival, reproduced.
- The unmutated self-tests at the head: `carry_audit self-test: 201 checks, 0 failed`, `cloud_relay self-test: 279 checks, 0 failed`.

## Figures

- `python3 -I tools/audit/carry_audit.py --self-test`: 201 checks, 0 failed at the head; 2 failed with main's `load_dests`.
- `bash tools/audit/seat/cloud_relay.sh --self-test`: 279 checks, 0 failed at the head (275 at main; the 4 added are the UNREAD arm).
- `python3 dev/audit/harnesses/r10_carry_parser_mutants.py B2-ancestry B2-always`: both killed, as listed under Mutation proof.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-34`: KILLED at the head, SURVIVED at main.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED`, running `tests/entities.py` (scope.run).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 -I tests/throwaway_git.py --check`: 0 raw git init or clone sites refused, 0 stale allow entries at HEAD.

## Red checks

none. No check is red on this head's ancestry that this seat could read: the Nightly workflow's latest scheduled runs on main concluded success (run 230, 2026-10-27), and prepr's ancestry-reds step had no pushed branch to read. If pr-contract lists one at the pull request, it is answered there.

## Unpinned sites

The one production line added in `load_dests` (the ancestry branch) is pinned by an in-tree mutant (B2-ancestry, B2-always), because the `mutation-autofix` lane mutates `custom_components/` only.

## Forward-carry

- Card 1 (tvofi 2026-10-24, standing roster seat retirement): `roster_queue.py` exists, but no beat job runs it. The job that reads the orchestrator's roster queue, runs each op with `--lint-cwd` at a fresh origin/main and `--push`, writes one digest line per op, and runs beside the seat for one cycle before the seat stops, belongs to the beat. The `standing-roster.md` edit goes with it. The owner's binding constraint travels with it: the work moves to a job, never into the orchestrator's turns. Carry: R10-ORCH-BEATD

## Friction

none
