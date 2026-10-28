Fix review: blocked 3133112f7e2869278f2524201ed0637990a09eab class-open: carry_audit.load_dests rc domain unpinned: mutant "== 1" to "!= 0" survives the self-test (201/0), yet turns a clone without origin/main from a pass into REFUSED
bus-nonce: c831213cd040f81ffa8dd4bd9e18e7bb

# Fix review -- PR #2903, R10-FLOW-ROSTER-FREEZE close-out (round 1)

Reviewed head: `3133112f7e2869278f2524201ed0637990a09eab` (GitHub `headRefOid` at the start and re-read before publishing). A detached worktree at that head, a second at origin/main `aaf8af512` (the merge base: the head already contains main), and a third for mutants. Nothing pushed to the branch.
Roles drift: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Claims re-derived (RESULT lines)

- RESULT carry_audit --self-test head: `201 checks, 0 failed`; main: `196 checks, 0 failed`.
- RESULT B2-ancestry: killed failed=2 (the two stale-tree checks); B2-always: killed failed=2 (the two null controls); M0 baseline failed=0. B2-ancestry is main's semantics (tree read), so this is also the failing-test-first figure the body quotes (201 checks, 2 failed): reproduced.
- RESULT cloud_relay --self-test head: `279 checks, 0 failed`; main: `275 checks, 0 failed`.
- RESULT cloud_relay-34 (#2792 R1) at head: KILLED (`279 checks, 3 failed`, the three UNREAD checks); at main with only the harness entry added: SURVIVED. #2792's survival reproduced, and killed.
- RESULT reviewer mutants on the UNREAD arm, all killed (ev/own_mutants.txt): R1 re-applied by hand: 3 failed. Drop the `cat-file -e` clause: 1 failed. Drop the fetch: 13 failed. `echo UNREAD; return 1`: 1 failed.
- Reviewer mutants on b2: drop the NOTE -> killed (1); show_roster at HEAD instead of origin/main -> killed (1); `== 1` -> `== 0` -> killed (4); **`== 1` -> `!= 0` -> SURVIVED (201 checks, 0 failed).**
- RESULT throwaway_git --check: `0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`; the new self-test arm builds its repo inside the existing `throwaway_git_init` scratch repo.
- RESULT ref_privacy --check: `28 file(s) with a push site, 12 guarded, 60 line(s) added since aaf8af512c1f judged, 0 refused`; the diff adds no push site, so PUSHERS owes nothing.
- RESULT merge-tree --write-tree origin/main head: rc 0, tree 9d3f36c9d, no conflict (no claim file touched).
- RESULT VERSION, manifest version, notes heading: untouched. structure.py: PASSED. closure select: MODE: SCOPED, 1 script.

## The blocking finding

The body states a third behaviour of the new predicate: "A clone without origin/main answers some other rc and also keeps its tree" (the code comment says the same). Nothing pins it. Replace `== 1` with `!= 0` (stale on any non-zero rc) and the self-test stays at 201/0. The behaviour that mutant changes is real. In a clone with no `refs/remotes/origin/main` (`git clone --single-branch` of the PR branch), `carry_audit.py check --body` on this PR's own body gives:

- head: `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`
- mutant: `carry_audit: REFUSED cannot list dev/programme/rosters/ at origin/main ... Not a valid object name origin/main`

pr-contract can reach this domain. Its main fetch is an earlier `if: always()` step. If that step fails, the carry step still runs, with no origin/main. The repair is one self-test case: in the scratch repo, `update-ref -d refs/remotes/origin/main`, then assert that a group in the tree passes with no NOTE. Add a mutant `B2-rc` (`== 1` -> `!= 0`) next to B2-ancestry. Carry: R10-FLOW-ROSTER-FREEZE

## Non-blocking notes (fix in the same re-cut if cheap)

- In a shallow clone, the predicate gives a false rc 1. Measured on a scratch repo with a depth-1 clone and origin/main = HEAD~1 fetched at depth 1: `merge-base --is-ancestor origin/main HEAD` returned rc=1, where the true answer is 0. A shallow HEAD that contains main therefore takes the stale-tree branch. It prints a false `lacks origin/main` and drops the tree's own new groups. Cloud seats start shallow, and INSTRUMENTS tells them to unshallow first. A `git rev-parse --is-shallow-repository` guard (shallow: keep the tree) closes it. The null control is the same scratch repo after `fetch --unshallow`, which returns rc 0. Carry: R10-FLOW-ROSTER-FREEZE
- The same applies wherever CI checks out a head that lacks main: a `workflow_dispatch` bot-head run, a re-run of an old merge ref, or main moving between the event and the fetch step. Those runs now read main's roster rather than the tree's. This is the intended P98 trade, and the round-ref union covers groups added through the roster branch. A PR whose own tree adds a group that is not on the round ref loses it there. The body's "CI's merge checkout keeps its tree" holds only for a fresh merge ref, and the body should say so. Carry: R10-FLOW-ROSTER-FREEZE

## Requirement table against main (verified)

- (a) review-in-flight freeze: 07cbe6fe1 is on main; HELD-REVIEW self-test checks are present; mutants cloud_relay-22..28 are in the harness. Met.
- P-H, HELD-VERDICT: on main with the four null controls (older head, blocked at head, no ref, exact-head mismatch). Met.
- Hold-file grammar: met on main (nine malformed variants, release file). The ROSTER-APPEND text is the group's 4th carry entry on the roster. Met.
- (b) round-ref read: c01d54b98 (#2779) is on main. Met.
- (b2): landed here except the rc-domain pin above.
- #2792 R1: killed here (above).
- Card 1: no beat or daemon job invokes `roster_queue.py` (grep of tick_loop.sh, daemonize.py and seat/*.sh is empty). The carry is already in the tree: R10-ORCH-BEATD carry 22, on both origin/main and the roster branch at b36710478. It states the precondition (a seeded no-op op lands, a seeded lint failure refuses, the seat runs beside the job one cycle) and the owner's no-inline constraint. Carry check (step 10): satisfied.

## Red checks (step 11)

`tests / nightly-status` is red at the head (job 122641850283). Its diff does not reach what nightly-status reads, so per step 11 it is not this PR's. All of the head's workflows have concluded; no check run is pending. Both `pr-contract / pr-contract` runs started after the red concluded at 05:02:24Z: 122653076099 (05:38:42Z) and 122653949333 (05:41:35Z). Both concluded success, and that run is the evidence. No root-cause class is owed.

## CI at the head (check-runs API, ev/checkruns_head.tsv)

Every check run has completed: gate success (two runs), pr-contract success (two runs), budget-raise-gate success, tests/closures, fast (3.14), coverage, coverage-ratchet, typing and mutation success, governance instrument-self-tests success, all three codeql/Analyze success. The only red is nightly-status (above). No heavy run was re-run here.

## Group close and #2389

- Once this merges with the rc pin, nothing of R10-FLOW-ROSTER-FREEZE's brief or its eight carries is owed in-group. Card 1 sits with R10-ORCH-BEATD. The group can go `done`. Its roster `resume` is stale ("dispatch arm (a) fixer" although arm (a) merged as 07cbe6fe1), which is the orchestrator's record to fix. Carry: R10-FLOW-ROSTER-FREEZE
- #2389 must not close on this group. Four other live groups list it in `issues`: R10-RCA-HEADMOVED (root-cause seat O15, not-started), R10-FLOW-BODY-ONLY, R10-FLY-ROW-HEAD-CARRY and R10-FLY-CARRY-DOC-CONTEXT. tvofi's 2026-10-18 record asks for a root-cause disposition (cause, cost test, countermeasure or a recorded refusal), and that belongs to R10-RCA-HEADMOVED. The cron's below-threshold comments (v7.0.1 to v7.0.5 windows) say explicitly that they are not a close. Carry: R10-RCA-HEADMOVED

Round: 1 of this PR.
