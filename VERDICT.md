Fix review: merge e71c999da56d58d8bff4cd639479826d9af1993d
bus-nonce: b967a70c89582135875675b14ecda440

# Fix review -- PR #2903, R10-FLOW-ROSTER-FREEZE close-out (round 2)

Reviewed head: `e71c999da56d58d8bff4cd639479826d9af1993d`. It was GitHub's `headRefOid` at the start and again before this post. I worked from a detached worktree at that head and ran mutants in two more detached worktrees at the same head. The harnesses mutate files in place, so the mutants ran on copies, never on the checkout under review. Each copy's `git status --short` was empty afterwards. Nothing was pushed to the branch.
Roles drift: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
This is round 2. Round 1 was blocked at 3133112f7 (`class-open`, B2-rc survived).

## Round-1 block: closed

- RESULT carry_audit --self-test at the head: `206 checks, 0 failed`. The body quotes the same figure.
- RESULT mutants, `r10_carry_parser_mutants.py M0 B2-ancestry B2-always B2-rc B2-shallow B2-shallow-always`. Every figure matches the body:
  - M0: `failed=0 baseline`.
  - B2-ancestry: `failed=2 killed`.
  - B2-always: `failed=7 killed`.
  - B2-rc: `failed=2 killed`. This is round 1's survivor.
  - B2-shallow: `failed=2 killed`.
  - B2-shallow-always: `failed=2 killed`.
- RESULT full census at the head: `sites=166 unmapped=0 mutants=237 survived=0`, rc 0. This matches the body.
- RESULT my own mutants on the b2 arm, each applied to a copy and checked with the self-test. All five were killed:
  - `show_roster` at `HEAD` instead of origin/main: 1 failed.
  - NOTE dropped: 1 failed.
  - Shallow test reads the rc instead of stdout: 2 failed.
  - `--is-ancestor` arguments swapped: 5 failed.
  - Guard inverted (`if shallow or ...`): 2 failed.
- RESULT end to end, on real clones of this repository with `carry_audit.py check --body <this PR's body>`:
  - Full clone, origin/main contained in HEAD (rc 0): `3 routed, 0 unrouted, 0 bad`, no NOTE.
  - `refs/remotes/origin/main` deleted (rc 128): `3 routed, 0 bad`, no NOTE. Under round 1's B2-rc mutant this case was REFUSED.
  - Depth-1 clone of the head, with origin/main fetched at depth 1: `--is-shallow-repository` is `true` and `--is-ancestor` gives rc 1, so the false answer is real. The guard keeps the tree: `3 routed`, no NOTE.
  - Full clone with origin/main at the real tip 6d86acc90 (rc 1): `NOTE stale tree: e71c999da... lacks origin/main 6d86acc90...; roster read at origin/main`, then `3 routed, 0 bad`.

## Body checks

- The corrected sentence: "a **fresh** merge ref contains origin/main and keeps the PR's own roster". It holds. `.github/workflows/pr-contract.yml` checks out with `fetch-depth: 0` (l75) and fetches `+refs/heads/main:refs/remotes/origin/main` (l426) before the carry step (l452). The body now names, as the stated P98 trade, the runs where the head lacks main. That covers both of round 1's non-blocking notes: the shallow guard landed, and the sentence is scoped.
- Class rule (step 6): I re-ran the body's seam enumeration, `sed -n '/^def load_dests/,/^def /p' ... | grep -nE 'git\(|subprocess\.run|returncode'`. It returns the same 7 lines the body dispositions: `ls-tree` and `show` (unchanged `--roster-ref` branch), the shallow test, the ancestry test, the two NOTE `rev-parse` calls, and the round-ref `--verify` (#2779). No seam is left open.
- Head figures (step 7): stamped at code head 09af90349 against edd7e0e14. The head e71c999da merges that code head and then origin/main 820b07eca. Main has since moved twice:
  - 6d86acc90, #2905: `tests/requirements-build.txt` and a delivery row.
  - 0b8f8b585: a triage file and a delivery row.
  
  Neither touches anything the figures read. The figures still hold: I re-took the self-test (206/0), the census (survived=0) and the B2 mutants at e71c999da, and each matches.
- cloud_relay (#2792 R1):
  - RESULT `cloud_relay.sh --self-test` at the head: `279 checks, 0 failed`.
  - RESULT `r10_seat_selftests_mutants.py cloud_relay-34`: `KILLED rc=1`. The harness's last-line field showed a `Terminated: 15` line from a background child, so I applied R1 by hand on a copy: `279 checks, 3 failed`. The three failures are the UNREAD checks ("a listed verdict ref the fetch cannot find freezes the head", "and says UNREAD", "a listed sha the fetched ref does not carry ... is UNREAD too").
- Other checks:
  - RESULT `throwaway_git --check`: `0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`.
  - RESULT `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - RESULT `closure.py select`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`.
  - VERSION, the manifest version, the notes heading and the golden and claim files are untouched.
  - No budget, closure, INERT or ledger number moves (step 14). The new mutants and self-test checks are earned by the predicate they pin.
- Forward-carry (step 10): unchanged since round 1, which verified it. Card 1 is R10-ORCH-BEATD carry 22. The group's stale `resume` is queued for the roster seat.
- Architecture (step 15): the guard stays inside `load_dests` and reads through `roster_lib.git_in` and `show_roster`. It adds no network fetch. The rejected alternatives are stated in the body.

## merge-tree (step 13)

`git merge-tree --write-tree origin/main e71c999da` gives rc 0:
- at 6d86acc90: tree 1ff84ad46.
- at the current main 0b8f8b585: tree e022a28fb.

No conflict, and no claim file is touched.

## CI at the head (check-runs API, ev/checkruns_head.tsv)

All 53 check runs at e71c999da have completed. Every conclusion is success or skipped, across both rounds of runs:
- gate: 122755393279, 122756097345.
- pr-contract: 122755140719, 122755827766.
- arch-score (two runs), budget-raise-gate (two runs).
- tests: closures, fast (3.14), coverage, coverage-ratchet, typing, mutation, graders-head-copy, lane-proofs.
- governance instrument-self-tests, the three codeql/Analyze runs, hassfest, validate-hacs.

`tests / nightly-status` (122744005411) is **green** at this head. The red at the previous head graded main and was answered in the body as not this PR's (step 11). No check is red at this head, so no root-cause class is owed. `tests / mutation` is green, but the diff writes no `custom_components/` line, so the lane drew no mutant. The in-tree mutants above pin the production lines, as the body's Unpinned sites section says. No heavy run was re-run here.

## Verdict

merge at e71c999da56d58d8bff4cd639479826d9af1993d. The rc domain is now pinned in every direction (0, 1 and 128, plus shallow and unshallow). Every named mutant and every mutant of mine is killed, the census shows survived=0, and the body's figures re-derive at the head.
