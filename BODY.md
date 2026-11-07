Part 2 of R10-TRAIN-MERGE-LOOP (#3242). Builds the train gate race hotfix and carries 3, 6, 7, 8, 9 and 16 (numbering per the #3242 fix review). origin/main (f2a015142714) was merged into the branch after #3256 landed; the merge was clean and pr_args.sh lost no line of either side. prepr.sh rc=0 at the merged head.

Carry N is the 1-based position in this group's carry list on the roster; the parent's numbers are noted.
- Carry 15 (the hotfix): `wait_ci` treats a red `gate` as pending while another workflow run at the same head is unfinished (read from actions/runs?head_sha, not check-run presence), then allows one poll for gate.py's rerun cascade. Bounded by the polls.
- Carry 1, Carry 8 and Carry 16 (parent carry 3): a bot tip whose pull_request runs are all approved is no longer refused; held, absent or unreadable runs keep the BOT_HEAD refusal.
- Carry 2 and Carry 10 (parent carry 6): `merge_train.py add --wait-post-approval [--poll] [--budget-hours]`, one module-level predicate (gate runs started at or after the approval, head pin, red refusal rc 2, budget rc 3). The verdict nonce is not checked: only the `Fix review: merge <head>` prefix from the approver bot.
- Carry 3, Carry 7, Carry 9, Carry 11 and Carry 17 (parent carries 7 and 17): `git_transient` classifier and `run_git_retry` (3 attempts) for every git fetch/push through `Train._reads_retried`; a rejection is never retried.
- Carry 4 and Carry 12 (parent carry 8): `pages()` in r10_codescan_wait_race.py falls back to per_page=30 after ghapi.get's own 5xx retries.
- Carry 5 and Carry 13 (parent carry 9): undraft only a head recorded `draft: true` at add; a failed ready or a re-draft is a Stop.
- Carry 6 and Carry 14 (parent carry 16): remerge_main.sh prints FAIL and `full log:` lines and keeps the push log when nothing was pushed.

## Head

c65cf1060e46db8d0abb9db7867380168326df43

## Mutation proof

Each mutant run with `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test`: hotfix, deferral check replaced by an empty list: 4 checks red (the #3248 scene, the TIMEOUT bound, the first-poll null control, the unreadable-listing arm). Carry 3, runs_approved forced False: the approved-runs arm red. Carry 6, started_at filter dropped: "only a pre-approval run is no re-run" red. Carry 7, git_transient forced False: the transient and retry arms red. Carry 9, recorded-at-admission condition dropped: "a head drafted after admission is not undrafted" red. Carry 8, fallback removed: harness --selftest crashes with ApiError 502. Carry 16, mut:remergegrep line deleted: the pr_args.sh arm red.

## Null control

Hotfix: a red gate with no unfinished sibling run still returns red on the first poll, and a failed unit beside an unfinished sibling is final. Carry 3: held, absent and unreadable runs still refuse with BOT_HEAD. Carry 6: add without the flag reaches train_add as before. Carry 7: a non-fast-forward rejection is one call. Carry 9: a non-draft head merges with no UNDRAFT line. Carry 16: a PUSHED stub keeps no log.

## Figures

- merge_train self-test: `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test` ends 0 failed at this head.
- pr_args self-test: `bash tools/audit/seat/pr_args.sh --self-test` was 0 failed after carry 16.
- Structure: `python3 tests/structure.py` passes, no budget changed.
- Not measured: the carry 3 count of BOT_HEAD stops since 2026-10-20 needs train logs this container does not have; the owner side can run it.

## Red checks

governance / instrument-self-tests: the main-wide 30-minute timeout, not caused by this diff. Carry R10-HOTFIX-SELFTEST-TIMEOUT. Cheaper detector: none beyond the self-test itself; the cost is the timeout, carried there.

## Forward-carry

none

## Friction

none
