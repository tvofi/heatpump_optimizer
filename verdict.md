Fix review: merge 763d98319f8a02bb0ef43eae1b22c0e7be7b77de

bus-nonce: fba6cb979cea3e2f3ff0f146e47dbcfa

Round: this is the third review of #3275. The first two blocked d6482b704 (X8) and a09ebaeb (W1), as their verdict comments show. The dispatch brief calls this one first-round. It is not the fourth, so fixer.md owes no re-cut. I reviewed head 763d98319f8a02bb0ef43eae1b22c0e7be7b77de from a detached worktree, against merge base 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76. The roles directory is current against main: its three-dot diff is empty.

## Findings

- Follow-up: pr_args.sh's `mut:unlock` arm is still a CPU-load race. It is one `kill -0` inside the lock holder's 0.2 s parent poll. Chaining the three pr_args.sh callers is a sound mitigation, not a cure. The count is now 26 of 26 chained: the body's 22, plus this head's CI run 42393030383 (its instrument-self-tests job logs `mut:unlock ... ok` and `pr_args self-test: 174 checks, 0 failed`), plus the three pr_args.sh waiters of my own replay. That bounds the rate only to below about 1 in 9 (95%, 3/26). The cure belongs to pr_args.sh, which is not this group's file. The carry is already on the roster: handoff/audit-r10-roster at cb42b64bd, R10-HANDOFF-PATH carry 19 ("From #3275, body item 097e824e"). It states its control, the unmutated holder still read alive, as finding-propagation.md requires. R10-HANDOFF-PATH is at stage carries-open, so it is still live. Carry: R10-HANDOFF-PATH
- `## Red checks` describes earlier heads (ec8c58a9 "no CI run exists", and a09ebaeb's job ids), not this head's runs. This head has one concluded red, `tests / nightly-status` job 128464907664. The body names that check and answers it as not this PR's, and the answer holds: the diff reaches nothing nightly-status reads (fix-review.md step 11). `pr-contract / pr-contract` job 128475915866 started at 17:32:47Z, after that red concluded at 16:51:17Z, and passed. Under step 11 that run is the evidence. This is wording only, owing no code change. Carry: dismissed: the head's only red is named and answered by check name, and the pr-contract run after it is green

## Evidence

- RESULT CI at the head: `merge_train.py classify 763d98319f8a02bb0ef43eae1b22c0e7be7b77de --pr 3275` printed `GREEN 763d98319f8a02bb0ef43eae1b22c0e7be7b77de pending: none red: none`, rc 0 (ev/classify-1.txt). All 55 check runs fit on one page (perPage 100). I read them by job. The one concluded failure is `tests / nightly-status` (see Findings). Both `gate` runs (128476322382, 128476115427) succeeded.
- RESULT real CI wall time, not a replay: `governance / instrument-self-tests` job 128464907715 (run 42393030383) is this head's first run of that job. It ran 16:52:08Z to 17:02:20Z, 612 s of the 1800 s timeout, which leaves 66% headroom (the brief asks for at least 30%). Before the fix, main took 1719 to 1785 s (the roster brief's four runs; cited, not re-timed by me). The job log ends `pr_args self-test: 174 checks, 0 failed`, then `bg_unread: 5 started, 0 unread`, then the runner's own "Cleaning up orphan processes". So the detached self-tests outlive their launcher step and are all read.
- RESULT harness at the head (`python3 dev/audit/harnesses/r10_selftest_timeout.py`, ev/harness-head.txt): M0 is 14 of 14 PASS. W2, M1, M2, X8, M3 and M4 are each KILLED, with the same killing arms the body lists. `RESULT survivors=0`, rc 0. M1 is killed by `refuse slow bad`, `refuse chained bad` and `refuse bad`. M2 is killed by `refuse chain killed` and `refuse killed`. This is the fixer's harness, disclosed as such. There is no finder harness: the finder's instrument is the job-timing read above, which I re-took at this head.
- RESULT failing first: the head's harness run against the merge base's workflow exits rc 1 (`StopIteration`: there is no launcher step at the base), in ev/harness-at-base.txt.
- RESULT reviewer's own instrument (mine/stub_replay.py, copied into ev/). It runs the real launcher, the five waiters and the bg_unread step exactly as GitHub does (`bash -e`, pipefail only where a step sets it), with the five detached commands swapped for 2 s stubs (ev/mine-stub-replay.txt and ev/mine-mutants-AD.txt):
  - The null control, with all five stubs passing, leaves the job GREEN.
  - Each of the five stubs failing in turn fails exactly its own waiter step, and the job goes RED.
  - W1 (the prepr waiter step deleted): the last step fails with `UNREAD prepr`, RED.
  - Mutant A (the update-pr `bg_wait` line replaced): `UNREAD update-pr`, RED.
  - Mutant D (the beatd waiter echoes a fake tally): `UNREAD beatd`, RED.
  - M1 planted in the real workflow's library leaves the job GREEN on a failing stub that prints a passing tally. That is the expected survivor: the harness arms kill M1 in the library.
- Focus checks (ev/step-names.txt):
  - No step or job is renamed. The job set is equal at base and head, and no base step name is gone: 100 steps become 102, adding only the launcher and the bg_unread step. The five waiters keep their names and their byte-identical tally greps.
  - `timeout-minutes` is 30 at both ends, so it is not raised.
  - bg_wait refuses a missing status (M2 is killed) and a missing pid file (`cat` fails under `-e`).
  - No step writes GITHUB_ENV or GITHUB_PATH, so the early launch loses no environment an in-line run would have had.
  - The prepr waiter now runs under `!cancelled()`, where the base's unconditioned step was skipped after an earlier red. That is more coverage, not less.
- Merge with main: `git merge-tree --write-tree origin/main HEAD` against origin/main aaaec2128 exits 0 (tree d4e8838524ea), with no MERGE-CLAIM line (ev/merge-tree.txt).
- Hygiene:
  - The three-dot diff touches only governance.yml, the new harness, dev/programme/delivery/3275.md (the delivery row is present) and tests/closures.json, where the new harness is listed, so the new file is classified.
  - No `*_budgets.json`, VERSION, manifest or RELEASE_NOTES.md is touched.
  - `## Head` names 763d98319, the head I measured, and it was still the PR's head at verdict time.
  - The packet reported no refusals: figure_lint 9 resolved, carry_audit 4 routed, 0 unrouted.
- RESULT my own re-run of the replay at the head (`python3 dev/audit/harnesses/r10_selftest_timeout.py replay .github/workflows/governance.yml bg`, ev/replay-head-bg.txt): `RESULT replay_seconds=681 failed=0`. Every step passed, the last step included. The body cites 616 s. The order matches, and my run took longer on this container. All three pr_args.sh waiters passed, so the chained `mut:unlock` count comes to 26 of 26 with this replay.
- Not re-derived by me:
  - W1's replay seconds (610 and 605 s). My own W1 check is the stub replay above.
  - The base replay's 1870 s and the main "before" job times. Both are cited.
  - The 1-in-9 concurrent `mut:unlock` failure count.
