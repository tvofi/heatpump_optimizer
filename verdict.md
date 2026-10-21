Fix review: merge 3f22a805c7ca335f15a6b218d6aa15a7cec8bb20

Round: 2. Round 1 blocked 50c4a681d on a surviving read-back retry-exhaustion mutant (`die` -> `break`). I reviewed from detached worktrees at 3f22a805c7ca335f15a6b218d6aa15a7cec8bb20 (head) and f2fb1b0e9 (merge base, which is origin/main). Just before writing this I re-read the head on origin with `git ls-remote`: it has not moved (ev/HEAD.txt). The role file is current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty. I read the group JSON and STUDY K14 at pin 78117030 (claude/dazzling-gauss-7l3u2b).

## RESULT lines
RESULT round-1 blocker: KILLED. The finder harness's `body_patch-1` (`die` -> `:` on the exhaustion guard) is KILLED at head: rc=1, `body_patch self-test: 62 checks, 3 failed`. My own R7 (`|| :`) and R8 (`rbok=1` from the start) are also killed, each failing on `REFUSE: no read-back can be performed (retry exhaustion)` (ev/harness_head.txt, ev/reviewer_mutants.txt).
RESULT finder harness r10_seat_selftests_mutants.py: at head, M0 has 0 seat steps red (this includes the new step `body_patch self-test: 62 checks, 0 failed`) and `RESULT survivors=0`. At base f2fb1b0e9: M0 0 red, `RESULT survivors=0`, and there is no body_patch step. Flat at both ends, nothing regressed (ev/harness_head.txt, ev/harness_base.txt).
RESULT self-test body_patch at head: 62 checks, 0 failed (ev/body_patch_selftest.txt). The body says 51. That was the round-1 count and is stale: round 2 added the rbfail, spaces and non-ancestor-base fixtures and the m7-m10 mutants.
RESULT self-test app_push at head: 135 checks, 0 failed. This matches the body, so the mint refactor changes no pinned behaviour (ev/app_push_selftest.txt).
RESULT selftest_wiring --check: 39 self-testing, 39 wired, 0 unwired at head; 38/38 at base. The body says 38/38, which is stale; its +1 claim holds (ev/tree_checks.txt).
RESULT structure.py: STRUCTURE RATCHET PASSED. closure select vs f2fb1b0e9: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. throwaway_git --check: 0 refused (ev/tree_checks.txt).
RESULT my mutation proof: 23 mutants, 21 KILLED. They cover the head check (both forms), the contract arm (die, lint rc, carry rc, return, fail-open check-run listing, dropped --red), the read-back (exhaustion x2, body, stale, verdict stale, eq1 always-true, tries=1), the pre-write re-read, dry-run fall-through, state!=open at step 2, and the token revoke and EXIT trap in the shared app_mint.sh. 2 SURVIVED, and neither blocks (Notes 1-2) (ev/reviewer_mutants.txt).
RESULT real arms, live read-only dry-run: I ran `--dry-run 2578 <head> <live body>` with curl write-guarded (PATCH/POST/DELETE/PUT refused, 0 attempted, 18 reads). The real policy_lint printed `PR-BODY: 0 error(s)` and the real carry_audit printed `3 routed, 0 unrouted`. The DRY-RUN line names the PATCH URL and payload. It took 6.5 s (target < 30 s). With a wrong expected sha it refuses before contract or mint, rc=1. With a `hello` body, policy_lint reports 8 errors and the tool refuses, `NEVER sent` (ev/live_dryrun.txt). No PR body was PATCHed.
RESULT merge-tree --write-tree origin/main(f2fb1b0e9) head: rc=0, tree 1d0aac83 -- clean (ev/merge_tree.txt)
RESULT VERSION / manifest / RELEASE_NOTES / golden + claim files / *_budgets.json / closures.json: untouched
RESULT class rule (from the body): `grep -rn "POST.*access_tokens" tools/pr tools/audit/seat | grep -v "STUB\|printf"` returns app_mint.sh, app_comment.sh and app_approve.sh. The last two mint the hpo-approver identity (identity-approver.pem); the only hpo-author.pem in app_comment.sh is a self-test fixture. Every seam is dispositioned and none is open (ev/class_rule.txt).
RESULT spec, checked one item at a time against the code:
- three positional args, plus --dry-run and --repo;
- live head == expected, before mint, contract or write (self-test: 0 curl, 0 node);
- contract = pr-contract's policy_lint argument set, plus `carry_audit.py check --body`;
- mint factored into tools/pr/app_mint.sh and sourced by both scripts; no copy, and no leftover $key/$appid/cleanup in app_push.sh;
- body read back modulo one trailing newline, with completed mismatches not retried;
- head re-read before the PATCH and on read-back;
- --dry-run prints the request and makes 0 curl calls;
- wired as a step in governance.yml instrument-self-tests, with an INSTRUMENTS.md entry;
- one `--once` unit whose last line is `body_patch: OK|REFUSE`.
All present.

## Step 11: checks at head (read once, 2026-10-21T17:34:47Z; ev/check_runs.txt)
24 success, 14 skipped, 1 neutral (CodeQL). Red: nightly-status only. The body's `## Red checks` names and answers it, it grades main, and the live policy_lint red-history pass accepted the body. pr-contract succeeded twice; the second run started 17:22:56, after nightly-status concluded red at 17:22:33. instrument-self-tests, mutation, policy-docs, fast (3.14), closure-scope and budget-raise-gate all succeeded. The diff writes no Python production line, so mutation drew no mutant on the shell. My targeted mutants above stand in for it. Still pending: Analyze (python) and coverage. I judged on the rest.

## Notes (not blocking)
1. Mutant R21 SURVIVED. Turning the read-back's `bad state=*) die` into `rbok=1; break` prints OK for a PR that closed or merged between the PATCH and the read-back, and no fixture closes the PR after the write. Plain deletion of that line (R23) is fail-closed: the case falls through to the retries and then the exhaustion die. The surviving path needs a close inside a window of about a second after a 2xx PATCH, so I don't block on it. It is a one-fixture repair if wanted.
2. Mutant R22 SURVIVED. Making the PATCH failure non-fatal is still fail-closed: the read-back then finds the old body and refuses with `not identical`. This is an equivalent outcome, not a gap.
3. The body is stale at this head and should be refreshed. `body_patch.sh` itself can do that without moving the head:
   - `## Figures` says 51 checks; the head has 62.
   - selftest_wiring says 38/38; the head has 39/39.
   - `## Mutation proof` says "Six of six arms" and does not mention the round-2 arms (rbexhaust, eq1, existing, threedot), including the round-1 blocker's.
   - The `## Head` second paragraph describes 18e7a7c6 as the code head.
   - `## Red checks` says "No other check has run: ... no pull request yet".
   - The first paragraph still calls #2560's 111->113 figure "the open case", which K14 revision 4 corrects.
   These are the fixer's own figures and I re-derived each one above. I am not confirming any of them as they are stated.
4. The tool does NOT pass `--roster-ref` to carry_audit. The dispatch's spec line asks for "carry_audit check --body with the roster ref". The pinned pack at 78117030, which this review is against, says only `carry_audit.py check --body`, and that is what pr-contract runs. Revision 8 on the pack branch, after the pin, asks for `--roster-ref <fresh roster branch>`. The script header documents the divergence: it reads the caller's worktree roster. If revision 8 binds, the follow-up is one argument plus one fixture.
5. The header line "It reads the repository from the worktree it runs in" is inaccurate. The repo comes from a hard-coded default or --repo, and only the contract reads the cwd's tools.
6. There is no Group line in the body. Per the brief this is a verdict note only.

bus-nonce: d495ed9002400d88ebb148c78bead593
