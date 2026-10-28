R10-FLOW-ROSTER-FREEZE close-out: what #2389 and the group's carries still required on main after arms (a) 07cbe6fe1, (b) 24b4399cf / 3d526a7f3 and #2779, and the two pieces this pull request lands. Refs #2389: the roster lists it under the group's `issues`, not `fixes`, so pr-contract leaves its disposition to the orchestrator once the group closes. #2389 stays open: R10-RCA-HEADMOVED and three other live groups list it.

Requirement by requirement, measured at origin/main 07295d4ea:

- (a) relay freeze while a review is in flight: met by 07cbe6fe1 (`review_freeze` and the handoff arm in `tools/audit/seat/cloud_relay.sh`), pinned by its self-test's `HELD-REVIEW` checks and mutants cloud_relay-22..28.
- P-H, freeze on a merge verdict at the live head: met by 07cbe6fe1 (`HELD-VERDICT`), with the four null controls the triage asked for in the self-test.
- Hold-file grammar and its ROSTER-APPEND text: the grammar is met (`hold_list`, nine malformed variants in the self-test), and the ROSTER-APPEND text is already the group's fourth `carry` entry on main's roster. Nothing is owed.
- (b) carry_audit reads the round's roster ref: met by #2779 (c01d54b98), pinned by the `load_dests reads the round ref` self-test checks.
- P98 arm (b2), stale tree: **not met on main**. `load_dests` read the tree's roster even when HEAD lacked origin/main. This PR lands it.
- #2792 review, mutant R1 in `review_freeze` survives: **not met on main** (it survives, see Null control). This PR adds the self-test arm that kills it.
- Card 1, retiring the standing roster seat: the runner exists (`tools/audit/seat/roster_queue.py`, d17df53c5), but no beat or daemon job invokes it, and the card's acceptance needs a live job beside the seat for one cycle. That is a beat job in R10-ORCH-BEATD's files (`daemonize.py`, `tick_loop.sh`), not this group's; it is already that group's carry 22 on main and on the roster branch. `standing-roster.md` is left alone, since the card puts its edit in whichever group merges later.

Change:

- `tools/audit/carry_audit.py` `load_dests`: with no `--roster-ref`, when `git merge-base --is-ancestor origin/main HEAD` answers rc 1 in a clone that is not shallow, the roster is read at origin/main through `roster_lib.show_roster`, printing `NOTE stale tree: <HEAD> lacks origin/main <sha>; roster read at origin/main`. Every other case keeps its tree, silently:
  - rc 0, HEAD contains origin/main.
  - rc 128, no origin/main in the clone (`git clone --single-branch`, or pr-contract's carry step after its `if: always()` main fetch failed).
  - a shallow clone (`git rev-parse --is-shallow-repository` prints `true`). Its walk stops at the graft and answers rc 1 for an ancestor it cannot reach. The cost, stated: a shallow checkout really behind main reads its own stale roster, as every checkout did before P98. INSTRUMENTS tells a cloud seat, which starts shallow, to `git fetch --unshallow` first.
- Which CI runs keep the tree: pr-contract checks out with `fetch-depth: 0` and fetches main, so a **fresh** merge ref contains origin/main and keeps the PR's own roster. A run whose head lacks main reads main's roster plus the round-ref union: a `workflow_dispatch` bot-head run, a re-run of an old merge ref, or main moving between the event and the fetch step. That is the intended P98 trade. A group the PR's own tree adds and the round ref lacks is not seen on such a run.
- Self-test, in a scratch repo built through `tests/throwaway_git.py`:
  - HEAD behind origin/main: a carry to a group that exists only on main passes, with the NOTE. A group on neither ref is still BAD (null control).
  - HEAD containing origin/main keeps the PR's own new group, with no NOTE (null control).
  - A depth-1 clone (`throwaway_git_clone`) whose HEAD contains origin/main, with origin/main fetched at depth 1, keeps the PR's own group with no NOTE. After `fetch --unshallow` the same carry passes with no NOTE (null control: the ancestry answers itself once complete).
  - With `refs/remotes/origin/main` deleted, the PR's own group passes with no NOTE.
  - A refusal from `load_dests` is caught and fails these checks by name, not by a crash.
- `tools/audit/seat/cloud_relay.sh` self-test: a verdict ref the listing names but the fetch cannot find, or a listed sha the fetched ref does not carry, is `UNREAD` and frozen. The same ref listed at its own sha, holding a verdict at an older head, freezes nothing (null control). No production line changes.
- Mutants in `dev/audit/harnesses/r10_carry_parser_mutants.py`: B2-ancestry, B2-always, B2-rc (`[0] == 1` to `[0] != 0`, the review's survivor), B2-shallow (guard off) and B2-shallow-always (guard always on). cloud_relay-34, the #2792 R1 mutant, is a per-file id placed inside the freeze block of `dev/audit/harnesses/r10_seat_selftests_mutants.py`.
- `tools/audit/seat/INSTRUMENTS.md`: the freeze paragraph names `HELD-UNREAD`.

Alternatives:

- For (b2), reading carry files at origin/main as well was rejected. The carry names the roster only, and a wider read would change which issues count as owned on a pull request's own tree.
- For the shallow guard, deepening the clone inside `load_dests` was rejected: a read-only audit tool would fetch from the network. Keying on rc alone was also rejected, because a shallow clone gives rc 1 both when HEAD contains main and when it does not.

## Head

09af9034966c97211c63293e877ec4956be663c9, measured against origin/main edd7e0e14e08279d0ddc53ec4fcc983570edf12a (2026-10-28T08:36Z, `date -u`); merge base 07295d4ea. It adds two commits to the reviewed head 3133112f7: 5c62def31 (the rc-domain pin, the shallow guard and its cases, B2-rc and B2-shallow) and 09af90349 (B2-shallow-always). No merge of main: `git merge-tree --write-tree origin/main HEAD` rc 0 at edd7e0e14 (fixer.md step 6).

## Mutation proof

`python3 dev/audit/harnesses/r10_carry_parser_mutants.py M0 B2-ancestry B2-always B2-rc B2-shallow B2-shallow-always`:

- M0: failed=0, baseline.
- B2-ancestry: killed, failed=2. `FAIL a tree behind origin/main reads the roster there: a group only on main passes`, `FAIL ... and says so: NOTE stale tree names HEAD and origin/main`.
- B2-always: killed, failed=7. It fails both "tree containing origin/main" checks, all three shallow checks and both "clone without origin/main" checks.
- B2-rc: killed, failed=2. `FAIL a clone without origin/main keeps its tree: the PR's own group passes`, `FAIL ... and prints no stale-tree NOTE`.
- B2-shallow: killed, failed=2. `FAIL a shallow clone whose HEAD contains origin/main keeps its tree: the PR's own group passes`, `FAIL ... and prints no stale-tree NOTE`.
- B2-shallow-always: killed, failed=2, the two stale-tree checks.

`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-34`: `KILLED rc=1 | cloud_relay self-test: 279 checks, 3 failed`.

## Null control

- Failing test first, for the shallow guard: the new cases on b9a66d28d's `load_dests` give `carry_audit self-test: 206 checks, 2 failed`, the two shallow checks. At the head: `206 checks, 0 failed`. The two no-origin/main checks pass on b9a66d28d too. They pin rc behaviour b9a66d28d already had, which only B2-rc tells apart, and that mutant is killed above. Re-taken at 09af90349 by the census: B2-shallow, which restores b9a66d28d's unguarded predicate, gives failed=2.
- The reviewer's measurement, reproduced end to end. Single-branch clone of the head, so `git rev-parse --verify -q origin/main` rc=1, then `carry_audit.py check --body <this PR's previous body>`:
  - head: `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`.
  - B2-rc applied by `sed` in that clone: `carry_audit: REFUSED cannot list dev/programme/rosters/ at origin/main ...`.
- First-round figures, on b9a66d28d's code. The (b2) arms on main's `load_dests` gave `201 checks, 2 failed`. cloud_relay-34 on main's self-test, run from a detached worktree of origin/main with only the harness entry added: `SURVIVED rc=0 | cloud_relay self-test: 275 checks, 0 failed`, the #2792 survival reproduced. This pass changes neither file those figures read.

## Figures

- `python3 -I tools/audit/carry_audit.py --self-test`: 206 checks, 0 failed at the head. 2 failed with b9a66d28d's `load_dests`, 201 checks at b9a66d28d.
- `bash tools/audit/seat/cloud_relay.sh --self-test`: 279 checks, 0 failed at b9a66d28d (275 at main; the 4 added are the UNREAD arm). Not re-run: this pass does not touch `cloud_relay.sh`.
- `python3 dev/audit/harnesses/r10_carry_parser_mutants.py` (no names, the whole census): `RESULT sites=166 unmapped=0 mutants=237 survived=0`; M0 `failed=0 verdict=baseline`. Null control: each B2 mutant's `failed=` is non-zero (Mutation proof above), so a census that ran no self-test could not print survived=0 beside them.
- Seam enumeration for the rc-domain class: every git call inside `load_dests` whose result picks a branch, from `sed -n '/^def load_dests/,/^def /p' tools/audit/carry_audit.py | grep -nE 'git\(|subprocess\.run|returncode'`. 7 lines:
  - `ls-tree` and `show` (the `--roster-ref` branch): not this diff's; its read is unchanged.
  - `rev-parse --is-shallow-repository`: closed in this diff, both directions (B2-shallow, B2-shallow-always).
  - `merge-base --is-ancestor`: closed in this diff, rc 0, 1 and 128 each a self-test case (B2-ancestry, B2-always, B2-rc).
  - the two `rev-parse` in the NOTE text: pinned by the `says so` check.
  - `rev-parse --verify` of the round ref: #2779's, pinned by its round-ref checks.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 1 script(s) run`, `tests/entities.py` (scope.run).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 -I tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`. The shallow case clones through `throwaway_git_clone`.
- `git merge-tree --write-tree origin/main HEAD`: rc 0 against edd7e0e14, so there is no conflict.

## Red checks

- `tests / nightly-status` is red at the previous head 3133112f7 (job 122641850283). It grades `main`, and this diff touches nothing it reads (`defect-root-cause.md`), so it is the orchestrator's on main.
- No other check went red on this branch's commits.

## Unpinned sites

The production lines added in `load_dests` are pinned by in-tree mutants, because the `mutation-autofix` lane mutates `custom_components/` only. They are the shallow guard (B2-shallow, B2-shallow-always) and the ancestry test (B2-ancestry, B2-always, B2-rc).

## Forward-carry

- Card 1 (tvofi 2026-10-24, standing roster seat retirement): `roster_queue.py` exists, but no beat job runs it. The job belongs to the beat. It reads the orchestrator's roster queue, runs each op with `--lint-cwd` at a fresh origin/main and `--push`, writes one digest line per op, and runs beside the seat for one cycle before the seat stops. The `standing-roster.md` edit goes with it. The owner's binding constraint travels with it: the work moves to a job, never into the orchestrator's turns. Already that group's carry 22. Carry: R10-ORCH-BEATD
- The group's roster `resume` still reads `next_step: dispatch arm (a) fixer`, which is stale: arm (a) merged as 07cbe6fe1. Two `set-resume R10-FLOW-ROSTER-FREEZE` ops (`next_step`, `note`) are queued on the orchestrator's roster queue for the roster seat. Setting the stage to `done` at this merge is the orchestrator's. Carry: R10-FLOW-ROSTER-FREEZE

## Friction

- fixer.md: cost: a host reboot killed this seat mid-census, and `dev/audit/harnesses/r10_carry_parser_mutants.py`, which restores the file it mutates only on a clean exit, left one generated LEAD-alternative mutant (`|minor\b` dropped) uncommitted in `tools/audit/carry_audit.py`. It was reverted by hand to the committed text before any figure here was taken: `git status --short` was empty, and the self-test gave 206/0 before the census ran. Carry: dismissed: a seat-side interruption, disclosed here; the restore-on-kill class went to the orchestrator as a proposal (to-main.txt)
