Part 2 of R10-TRAIN-MERGE-LOOP (#3242). Builds the train gate race hotfix and carries 3, 6, 7, 8, 9 and 16 (numbering per the #3242 fix review). origin/main (f2a015142714) was merged into the branch after #3256 landed; the merge was clean and pr_args.sh lost no line of either side. prepr.sh rc=0 at the merged head. origin/main (b4ec2f332fe3) was then merged again at 624b03fd0, clean, before the delivery row.

Carry N is the 1-based position in this group's carry list on the roster; the parent's numbers are noted.
- Carry 15 (the hotfix): `wait_ci` treats a red `gate` as pending while another workflow run at the same head is unfinished (read from actions/runs?head_sha, not check-run presence), then allows one poll for gate.py's rerun cascade. Bounded by the polls.
- Carry 1, Carry 8 and Carry 16 (parent carry 3): a bot tip whose pull_request runs are all approved is no longer refused; held, absent or unreadable runs keep the BOT_HEAD refusal.
- Carry 2 and Carry 10 (parent carry 6): `merge_train.py add --wait-post-approval [--poll] [--budget-hours]`, one module-level predicate (gate runs started at or after the approval, head pin, red refusal rc 2, budget rc 3). The verdict nonce is not checked: only the `Fix review: merge <head>` prefix from the approver bot.
- Carry 3, Carry 7, Carry 9, Carry 11 and Carry 17 (parent carries 7 and 17): `git_transient` classifier and `run_git_retry` (3 attempts) for every git fetch/push through `Train._reads_retried`; a rejection is never retried.
- Carry 4 and Carry 12 (parent carry 8): `pages()` in r10_codescan_wait_race.py falls back to per_page=30 after ghapi.get's own 5xx retries.
- Carry 5 and Carry 13 (parent carry 9): undraft only a head recorded `draft: true` at add; a failed ready or a re-draft is a Stop.
- Carry 6 and Carry 14 (parent carry 16): remerge_main.sh prints FAIL and `full log:` lines and keeps the push log when nothing was pushed.

## Head

35fc2646348b9c4d69a3b56b6452ff4075289807

Body-only re-take at the unchanged PR head: no code moved since code handoff c65cf106; 35fc2646 is that handoff merged with origin/main (624b03fd0) plus the delivery row (dev/programme/delivery/3288.md). Every figure below was re-run at 35fc2646.

## Mutation proof

Each mutant run with `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test`: hotfix, deferral check replaced by an empty list: 4 checks red (the #3248 scene, the TIMEOUT bound, the first-poll null control, the unreadable-listing arm). Carry 3, runs_approved forced False: the approved-runs arm red. Carry 6, started_at filter dropped: "only a pre-approval run is no re-run" red. Carry 7, git_transient forced False: the transient and retry arms red. Carry 9, recorded-at-admission condition dropped: "a head drafted after admission is not undrafted" red. Carry 8, fallback removed: harness --selftest crashes with ApiError 502. Carry 16, mut:remergegrep line deleted: the pr_args.sh arm red.

## Null control

Hotfix: a red gate with no unfinished sibling run still returns red on the first poll, and a failed unit beside an unfinished sibling is final. Carry 3: held, absent and unreadable runs still refuse with BOT_HEAD. Carry 6: add without the flag reaches train_add as before. Carry 7: a non-fast-forward rejection is one call. Carry 9: a non-draft head merges with no UNDRAFT line. Carry 16: a PUSHED stub keeps no log.

## Figures

- merge_train self-test: `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test` prints `519 checks, 0 failed` at this head.
- pr_args self-test: `bash tools/audit/seat/pr_args.sh --self-test` prints `177 checks, 0 failed` at this head.
- Structure: `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED at this head, no budget changed.
- Not measured: the carry 3 count of BOT_HEAD stops since 2026-10-20 needs train logs this container does not have; the owner side can run it.

## Red checks

Read from check-runs filter=all at 35fc2646 (both pages, 142 runs) and actions/runs?head_sha. CI code run 42386285946: attempt 1 cancelled by the owner at 15:52Z, attempt 2 (16:07Z) holds the reds below, attempt 3 (owner re-run, 18:39Z) is re-running tests / coverage as check-run 128492818833. None is caused by this diff, which touches only seat tooling (merge_train.py, pr_args.sh, remerge_main.sh, one harness, the delivery row).

- tests / coverage (check-run 128454571205): class runner stall. Started 16:12:32Z, concluded failure 17:21:35Z (1h09m, inside the job's 90-minute timeout-minutes, so the 30-minute cure of R10-HOTFIX-SELFTEST-TIMEOUT, #3275, does not apply: that timeout is the instrument self-tests', not coverage's). Annotation: "The hosted runner lost communication with the server"; no job log is served. Needs a re-run at this code head; attempt 3 (128492818833) is that re-run, already dispatched. Cheaper detector: none exists; a lost runner is GitHub infrastructure and no in-repo check can see it before it happens.
- tests / coverage-ratchet (check-run 128473127824): class consequence of the coverage stall. "Unable to download artifact(s): Artifact not found for name: coverage-json": coverage died before its upload. Clears with the coverage re-run. Cheaper detector: none exists; it is downstream of the same stall.
- tests / nightly-status (check-runs 128447471717 and 128454570948): class main-graded reporter. NIGHTLY FAILED graded verification dispatch run 42369836867 on main head 08fd676 (mutation-ledger 1-4, mutation-ledger-push, mutation-nightly, slow, all concluded cancelled). The diff touches no path the nightly lanes run or read (production code, mutation ledger, slow suite). The later verification dispatch, Nightly run 42382408131 (workflow_dispatch, head a37c58e), concluded success at 18:28:34Z. Cheaper detector: none exists for a cancelled main-side dispatch; it is graded on main, not this head.
- pr-contract / pr-contract (check-run 128474383637): class body gap. The kept body did not name tests / coverage and tests / coverage-ratchet; this body names both. Cheaper detector: `tools/pr/prepr.sh --body-check`, standing cost one run per body push; it was not re-run after attempt 2 turned red.
- gate (check-runs 128474546962, 128451186144, 128448800913): class aggregate. 128474546962 (run 42386285946 attempt 2) prints only `FAIL pr-contract / pr-contract: failure (this run)`. 128448800913 (CI edit run 42386286414) and 128451186144 (CI edit run 42387690111) print `FAIL tests / fast (3.14): cancelled (run 42386285946)`: a stale cross-run read of attempt 1 that the owner cancelled, not a deferral. Cheaper detector: none beyond gate itself; each clears when its upstream does.
- Cancelled at this head, not failures: attempt 1's jobs (tests / fast (3.14), tests / coverage 128448419981, governance / instrument-self-tests 128447471638, governance / env-matrix, tests / closures, tests / browser and the seven downstream lanes), each annotated "The run was canceled by" the owner. The earlier body's instrument-self-tests timeout entry does not appear in pr-contract's red-history across the 11 commits and is dropped.

## Forward-carry

none

## Friction

none
