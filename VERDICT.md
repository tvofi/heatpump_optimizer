Fix review: merge e9c0092e27e91e4b1d23178fc75774e5798dcc22

bus-nonce: 6d05bc1b8b5328c49d1f245f4520d40c

Round 2. Round 1 was `Fix review: blocked 1e6e79caa harness: replay-fails-open` (comment 6258763498). I measured head e9c0092e27e91e4b1d23178fc75774e5798dcc22 (ev/HEAD). It was still the branch head at verdict time, with main at dd27e7c1b (ev/heads_at_verdict.txt). `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Round 1's finding: closed
- Live control, run with this container's own failing gh (HTTP 403, a real failure, not a shim), in ev/replay_live_gh_failing.txt:
  - The new file prints `gate : STOP read: gh pr view headRefOid failed (rc=1): HTTP 403 ...` for #2401, #2373 and #2368, with no `path :` line, and exits rc=1.
  - 86cecbf07's copy, given the same gh, prints `#2368 head HTTP 403: Gi base fatal: Not a` / `0 raise(s), HOLDS`, rc=0. That reproduces round 1's defect, and the fix removes it.
- `--self-test`: 7 checks, 0 failed, rc 0 (ev/replay_selftest.txt).
- The body's mutants (ev/mutants_S.txt):
  - M0: merge_train 189/0, pre-flight 36/0, replay 0 failed.
  - S1 fails exactly 2: the fetch arm and the diff arm.
  - S2 fails exactly 2: the non-hex head arm and the non-hex base arm.
  - This matches the body, including its account of why S1 leaves the gh and merge-base arms standing.
- My own mutants on the replay (ev/mutants_reviewer.txt):
  - S3, where the ReadFailed handler returns 0: fails 6.
  - S4, where `git fetch` goes back to an unchecked `t.run`: fails 1.
  - S6, where merge-base uses `read` and not `sha`: fails 1.
  - S5, where `main` drops `rc |=` so a failed read exits 0: **survives the self-test** (0 failed, live exit 0). The self-test drives `replay()`, never `main()`, so the docstring's "the exit status is 1" is not pinned. I confirmed it live (rc=1 above). Not blocking: the printed reading, which was the defect, is pinned, and no caller keys on the exit code. A main-level arm is a one-line follow-up.
- Class rule (body step 8): `git grep -nE 't\.out\(|\.out\("'` on the replay returns 0 lines at the head and 2 at 86cecbf07. Every remaining `t.run` call goes through `read()`, or is the BASE shim or the reset (ev/head_checks.txt).
- `is_sha` is the train's own (`len==40 and set<=HEX`), so there is no second grammar.

## Re-verified at this head
- Self-tests (ev/selftests.txt):
  - merge_train 189/0
  - queue_pre_flight 36/0
  - budget_raise_gate 235/0
  - merge_pr.sh 12/0
  - proof_watch 34/0
  - agreement.mjs --self-test 27 of 27
  - the agreement pair `budget-raise: 2 readers, 56 items, 0 divergent`, AGREEMENT ok
  - STRUCTURE RATCHET PASSED
  - tmp_paths 0 refused
  - ALL 109 HARNESS HEADER CHECKS PASSED
  - DELIVERY STATUS OK, 0 overdue.

  These match the body.
- The train, pre-flight and gate code is unchanged since 86cecbf07, and merge_pr.sh and proof_watch since dcd012deb: both diffs are empty (ev/head_checks.txt). Round 1's P1, J1, W1, H1, U1, R1, T1, B1, Q1 and agreement-P1 measurements therefore carry.
- merge_pr.sh mutants that round 1 did not re-run (ev/merge_pr_mutants.txt):
  - M1 kills "expired mandate" and "mandate that does not exist".
  - M2 kills "no --mandate" and "non-id --mandate".
  - B1' kills "the owner body ... cites exactly the mandate given". My first spelling of B1' was void: printf recycled its format, so the id still printed. I re-cut it, and the re-cut is the result above.
  - D2 was not run.
- Merges:
  - `git merge-tree --write-tree origin/main(dd27e7c1b) e9c0092e` exits 0 (ev/merge-tree.txt).
  - No resolution delta (ev/resolution_delta.txt). e9c0092e's tree f595c0b0 equals the automatic merge of 6046ea608 and dd27e7c1b. 6046ea608's tree equals the automatic merge of 1e6e79ca and 35c0b69f. 3ab409ce's tree equals the automatic merge of 1e6e79ca and fa424fd9.
- VERSION, the manifest, the RELEASE_NOTES heading and tests/golden are untouched in the three-dot diff (ev/version.txt is empty).
- Forward-carry: unchanged since round 1, which verified it (INSTRUMENTS.md, and bugclasses.json I4).

## CI on this head (check-runs API; ev/ci_reds.txt)
- 7 red runs, and I read each log. All are infrastructure: the GitHub Actions installation API rate limit.
  - pr-contract ×2: the body fetch got HTTP 403, so /tmp/pr-body.md was missing.
  - arch-score ×2: HTTP 403 reading pulls/2421.
  - validate-hacs: GitHubRatelimitException.
  - env-matrix: its one failed arm is "GitHub API is unreachable ... UNCHECKED".
  - nightly-status: NIGHTLY UNREADABLE, HTTP 403.
- None is caused by this diff. `nightly-status` is not this PR's in any case (step 11).
- Not concluded at read: coverage, Analyze (python).
- Green: fast, typing, mutation, closure-scope, budget-raise-gate ×2, instrument-self-tests, delivery-status, wave-script, policy-docs, briefs, browser, hassfest.
- Step 11 is not ripe. Workflows have not all concluded, and no pr-contract run has read the body: both failed before the read. So I cannot post `root-cause-unanswered`. After the 04:00Z reset, the orchestrator still owes a rerun. Any red still standing after that rerun must be named in `## Red checks`. The body's current `## Red checks` speaks only to 1e6e79ca, not to this head.

## Not verified
- The replay's healthy-gh readings (review and mandate half) for #2401, #2373 and #2368. gh is unusable in this container.
- merge_pr.sh D2.
- coverage and Analyze (python) conclusions.
- The RCA demo.out sha1, which is out of tree.
