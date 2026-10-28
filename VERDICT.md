Fix review: blocked e4b3e01abb48644841202e7d7b0ae93107258bd3 mutant-survives: the retry budget is unpinned, an unbounded-retry mutant passes all 206 checks because the spent-budget fixture's fourth stderr is unclassified, not transient

bus-nonce: dc353331c0736bde6c26e8e29ce6b633

Round: first review of this head (round 1). Reviewed from a detached worktree at `e4b3e01abb48644841202e7d7b0ae93107258bd3`, merge base `5a755f53efda8c099af7d6a98fb0b22828a0593c`. `dev/governance/roles/` on main is unchanged since the merge base (empty three-dot diff), so the contract I followed is current. The finder's harness is the group brief's null control (5), read from `origin/handoff/audit-r10-roster` at `a1a3a9c0c`.

## Block

1. **mutant-survives (the backoff is not bounded by any test).** The brief requires "a stub failing 4 times refuses after the budget, naming the last error". The body claims null control (c) does this, "Four transient failures refuse after exactly 4 calls". The `rspent` fixture's fourth queued line is `gh: Service Unavailable (HTTP 503) the-last-one`. `gh_transient`'s sed (`^gh: (.*\()?HTTP ([0-9]{3})\)?$`) does not match it because of the trailing text. No status is extracted, the transport grep fails, and the line classifies as **refuse**; I confirmed this by calling `gh_transient` directly (`ev/budget-unpinned.txt`). So `rspent` refuses on an unclassified stderr at try 4, not on the spent budget. The "(after 4 attempts)" text appears only because `_try` happens to be 4.
   - Mutant R11 changes `[ "$_try" -ge "$READ_TRIES" ]` to `[ "$_try" -ge 999 ]`, which is effectively unbounded. It runs `206 checks, 0 failed`, rc=0.
   - Mutant R1 changes `-ge` to `-gt`, a 5-read budget. It also runs `206 checks, 0 failed`.
   - The production code is correct: a real `gh: Service Unavailable (HTTP 503)` classifies transient. Only the pin is vacuous.
   - Fix: make the fourth line a real transient shape (e.g. `gh: Service Unavailable (HTTP 503)`, and keep the last-error assertion on it). Optionally add a fifth queued transient so that budget+1 is killed by a call count of 4. Then re-run R1 and R11.
2. **root-cause-unanswered: `pr-contract` went red, unanswered.** Both `pr-contract` runs on this head concluded `failure`: job 119527655690, and job 119538432191, which started 23:08:56Z after every other workflow on the head had concluded. The log ends `BAD-DEST body item 0e5922c7: R10-FLY-GH-READ-RETRY: R10-FLY-GH-READ-RETRY is not a group of the roster` / `CARRY-AUDIT: 2 finding item(s): 1 routed, 0 unrouted, 1 bad destination(s)`. The body's `## Red checks` names only `nightly-status` and main's `ci-ratchet`. The cause is that CI's carry_audit reads main's rosters, where the fly-in group is not yet registered; it is on the handoff roster. Against `--roster-ref origin/handoff/audit-r10-roster` it routes cleanly (Evidence). The body still owes the answer (fix-review.md step 11).

## Findings

- The `rspent` fixture's fourth stderr line, `gh: Service Unavailable (HTTP 503) the-last-one`, is not a gh stderr shape and classifies non-transient. Null control (c) and the brief's budget-exhausted control are therefore unmet, and budget mutants R1 and R11 survive. Fix in this PR as described under Block 1. Carry: R10-FLY-GH-READ-RETRY
- `pr-contract` is red on this head with `BAD-DEST` for `Carry: R10-FLY-GH-READ-RETRY` (main's roster lacks the fly-in group), and the body's `## Red checks` does not name or answer it. Answer it in the body (the cheaper detector or that none exists), or route the carry to a destination main's roster knows. Carry: R10-FLY-GH-READ-RETRY

## Evidence

- RESULT head self-test `e4b3e01a`: `app_approve self-test: 206 checks, 0 failed`, rc=0 (`ev/selftest-head.txt`). Re-derived.
- RESULT base self-test `5a755f53`: `171 checks, 0 failed`, rc=0 (`ev/selftest-base.txt`). Re-derived.
- RESULT failing test first: the base production script with the head's self-test runs `206 checks, 16 failed`, rc=1, every one a retry arm (`ev/selftest-hybrid-base-script-head-tests.txt`). Re-derived, matching the body's 16.
- Mutation proof, my own runner (`ev/mutants.txt`; file restored, `git status` clean):
  - M0 null: 0 failures.
  - Killed, matching the body's counts: M1 15, M2 9, M4 2, M5 5, M6 1, M7 2, M8 5.
  - My extra mutants killed: R2 (429 not transient) 2, R3 (5xx not transient) 9, R4/R5/R6/R7 (each of the four call sites reverted to a bare `gh api`) 2/2/4/8, R8 (no sleep) 2, R9 (every stderr transient) 1, R10 (secondary-limit match dropped) 2.
  - **Survived: R1 (budget 5) and R11 (unbounded)**, 0 failures each (Block 1).
  - M3 (retry the POST) I did not re-run as written. The `post502` arm asserts 1 POST and no settle, and its count matches the body's 3 assertions.
- Brief checks: the four reads (the pull request twice via `check_pr`, the comments, CODEOWNERS, the files) all go through `gh_read`, and R4 to R7 show each is pinned. A 404, 401, 422 or permission 403 is not retried (M2/M4 killed). The backoff is bounded in code (`READ_TRIES=4`, 5/15/45 s), but no test pins the bound (Block 1). A primary-rate-limit 403 (`API rate limit exceeded`) classifies refuse, consistent with the brief's "secondary-limit 403" only.
- Figures at this head:
  - Seam rule `awk ...`: 10 lines (`ev/seams.txt`). Re-derived; every line is dispositioned in the body's table.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`. Re-derived.
  - `score.py --diff`: `Architecture score: dS +0.0000 NULL`. Re-derived.
  - `closure.py select`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` Re-derived.
  - `policy_lint.mjs --budgets`: rc=0. Re-derived.
  - `ci_predict.py` and the `run_always` lines: not re-run, so not re-derived here.
  - The 2667 s / train 8 figures come from the brief's train logs, which are not in this container: not re-derivable.
  (`ev/figures.txt`)
- Merge: `git merge-tree --write-tree origin/main e4b3e01a` gives clean tree `b46b5b4be9`, rc=0 (`ev/merge-tree.txt`). No claim file and no VERSION, manifest or notes heading is touched (the CI `no version edit` line agrees).
- Carry audit (standing rule 19): `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check` over the body gives `2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)` (`ev/carry-audit-body.txt`). Without `--roster-ref`, as CI runs it, it reports 1 bad destination (`ev/carry-audit-body-noref.txt`), which is Block 2. The forward-carry of the JWT `curl` GET and the carry path's `git fetch` is present in the roster group's `carry` list.
- CI on this head, check-runs API (49 runs): `instrument-self-tests` (which runs this self-test), `closures`, `mutation`, `fast (3.14)`, `typing`, `coverage`, `arch-score`, `budget-raise-gate`, `policy-docs` and the CodeQL analyses all passed. Red runs:
  - `pr-contract`: 2 runs, both failure (Block 2).
  - `nightly-status`: failure. It grades main, not this PR, and the diff reaches nothing it reads.
  - `ci-ratchet`: skipped on this head.
- Head: `e4b3e01abb48644841202e7d7b0ae93107258bd3` is the PR head, and the head in the body. I re-read it before writing this verdict (`ev/HEAD.txt`).
