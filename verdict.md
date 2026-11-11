Fix review: blocked 588d1a4dfe607bc990fb3ced410a1df98005b9cf mutation-vacuous: merge_train.py Train.pages key-dropped and the per-site --jq keys (check_runs, workflow_runs x2, jobs) survive 611/0

bus-nonce: 9303c424369010310d5b8f513ef03c0c

Round 1 of this pull request. Measured head 588d1a4dfe607bc990fb3ced410a1df98005b9cf, which is still `refs/pull/3462/head` when this verdict was written. Merge base ee64358be7eeccaec5178a923cb3b83a18a924a0.

## Block

The merge train's object-page reads take their list key from the `key` argument (`--jq .<key>[]`). No merge_train check pins that key: the self-test stubs answer one JSON item per line whatever `--jq` the call carries. Each of these production mutants passes `python3 tools/audit/seat/merge_train.py --self-test` with `611 checks, 0 failed`, rc 0:
- `Train.pages`: `gh_read.read_pages(self.run, path, key)` changed to `gh_read.read_pages(self.run, path)` (ev/mutant-pages-drop-key.txt)
- `_check_runs`: key `"check_runs"` changed to `"checkruns"` (ev/mutant-key-typos.txt)
- `bot_head`'s pull_request runs read: `"workflow_runs"` changed to `"workflow_run"`
- `_gate_busy`'s ci.yml runs read: `"workflow_runs"` changed to `"runs"`
- the infra re-run jobs read: `"jobs"` changed to `"job"`

These mutants are not equivalent. With the `_check_runs` typo, the finder's harness at this head, `merge_train.py classify 381b01147f24f36f474c443406b908028ca021f2 --pr 3427`, prints `REFUSE ci: the check runs at 381b01147f24 could not be read`, rc 2 (ev/mutant-checkruns-typo-live-classify.txt). That is the base's failure, the one this PR exists to fix. Only a live run of the classify harness catches it, and no committed check does. gh_read's own self-test does check the `--jq` expression, but only for `read_pages` called directly. The PR's merge_train mutant (`_check_runs` reverted to `--paginate`) is killed only by the `page=`/no-`--paginate` argv check, and that check ignores the key.

Remedy, kept to what the block needs: make the merge_train stubs (and queue_pre_flight's and orchestrator_tick's stubs for the paged reads) honour the call's `--jq`. For example, serve the object page `{"check_runs": [...]}` and refuse any `--jq` other than `.<expected key>[]`, as gh_read's `server` stub already does. Then re-run the five mutants above, and expect each to be killed.

## Evidence

- RESULT finder-harness base ee64358b: `classify 381b0114 --pr 3427` gives `REFUSE ci: the check runs at 381b01147f24 could not be read`, rc 2. Null control `classify --main ee64358b` gives `WAIT ... pending: gate`, rc 3 (ev/finder-harness.txt).
- RESULT finder-harness head 588d1a4d: `classify 381b0114 --pr 3427` gives `GREEN 381b01147f24f36f474c443406b908028ca021f2 pending: none red: none`, rc 0. Null control: identical to the base, `WAIT`, rc 3. The fix moves the harness, and the one-page control does not move.
- Not re-derived: the body's check-runs `total_count` figures (112 and 44). This seat has no unrestricted `gh api`. The harness moving at the multi-page commit and staying flat at the one-page commit is consistent with those figures.
- Self-tests at the head (ev/selftests-head.txt): merge_train 611/0, gh_calls 215/0, gh_read 146/0, tick_loop 30/0, beatd 123/0, queue_pre_flight 53/0, orchestrator_tick 312/0. The body's 308 was measured at 1820d2d5, before the main merge ee64358b, so this figure was not compared. Also at the head: agreement `AGREEMENT ok`, `STRUCTURE RATCHET PASSED`, and `MODE: SCOPED -- 1 script(s) run`.
- Reviewer mutants (ev/mutants.txt) killed: read_pages accumulation, max_pages truncation, unparseable page read as empty, runs_approved on an empty listing, gate_deferred counting completed runs, the pre-flight comments failure ignored, gh_calls `--top` rc 3 changed to 0, the seat-gh unmodified predicate dropped, the seat-gh admit disabled, the TICK-GH printf disabled, and beatd seat_bin's env var renamed.
- Reviewer mutant survived and is equivalent: tick_loop.sh's `export PATH` deleted. PATH is already an exported variable of the shell, so the prepend reaches the children without that line. Carry: dismissed: evidence, not a finding
- The body's own mutants: its named in-tree arms are confirmed killed by the self-tests above. Its listed survivors (MAX_PAGES, slice widths, scaffolding) were not re-run.
- Class enumeration (`git grep -c -e '--paginate' -- tools tests ':!*.md'`): 74 lines in 28 files at 45a8b828 and at ee64358b, and 66 in 27 at 1820d2d5 and at the head (ev/class-enum.txt). These match the body. merge_train.py and queue_pre_flight.py keep only docstring and self-test matches.
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched against the merge base (ev/version-untouched.txt is empty). No claim file was touched.
- `git merge-tree --write-tree origin/main 588d1a4d` gives rc 0, a clean merge (ev/merge-tree.txt).
- Body head: it names 588d1a4dfe607bc990fb3ced410a1df98005b9cf, which matches the head measured here.
- CI: `merge_train.py classify 588d1a4d --pr 3462` printed `WAIT 588d1a4dfe607bc990fb3ced410a1df98005b9cf pending: gate red: none` on every poll from 12:00Z to 12:17Z (ev/classify-rc.txt). No red was concluded, so `## Red checks: none` is not contradicted at this time.
- The forward-carries are both `dismissed:`. carry_audit at the head reports 2 routed and 0 unrouted (review packet).

## Findings

- The seat-gh admit's "tracked and unmodified" predicate compares against the checkout's own HEAD. A gh_comment.py whose mandate_guard was removed in a local commit is therefore admitted. Part 1's registered-worktree rule had the same reach, and the guard is deny-by-default against an accidental raw post, not a same-user adversary. Carry: dismissed: pre-existing reach under part 1's rule; the shim guards against accidental posts by the same user, not a committed bypass

## Friction

none
