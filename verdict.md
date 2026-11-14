Fix review: blocked a55158085ed8cd6517113af8b77af07492a6634e mutation-vacuous: red_carried_to_next_cycle, no_per_run_remember survive the self-test at this head

bus-nonce: 0d3ded9ecb243616598dc79e980061a4

## Block

- mutation-vacuous (fix-review.md step 1). The delta (2fb2c7f0) moves the RED lines and the run list from locals into persisted memory. Two of its new properties are not pinned. I ran `python3 -I tools/audit/seat/beat_jobs.py --self-test --no-mutants` on each mutant at this head, and both of these give rc=0 (ev/mutants.txt, driver ev/my_mutants.py):
  - red_carried_to_next_cycle: a new cycle starts with `"red": mem.get("red", [])` instead of `[]`. Every later cycle then re-reports the earlier cycle's REDs, including after the fix lands. That is the false red the row exists to avoid, and it hides the RED-then-gone signal the body's GREEN run demonstrates. The test "a completed cycle starts the next one at the newest tip" checks only the worktree add for tipb. Nothing reads the digest of the second cycle. Pin it with a case that finishes a red cycle at tipa, then a green cycle at tipb, and asserts that the digest is empty.
  - no_per_run_remember: the per-run `ctx.remember(...)  # after every run: a killed pass keeps what it ran` becomes a no-op. The body's Limits bullet depends on this line. The self-test that runs past a pass is killed, and the runs before it in that pass stay done. Without the line, a killed pass loses its whole pass, and a repeat kill makes no progress. No case kills a pass partway through. Pin it with a case where `ctx.run` raises, or the process dies, after N runs, and the next pass does not run those N again.
  With both pinned and the code unchanged, this delta is mergeable on everything else I checked (see Evidence).

## Findings

- The detection-lag and refused-opens-per-Darwin-red measures are owed at round end, as the body says. Carry: O1
- Out of scope: the stale-worktree remove before `worktree add` survives deletion (my mutant no_stale_wt_remove, rc=0). The line is unchanged since 8a05961b, so it is outside this delta. With resumable passes a killed pass is now an expected path, so it carries to the orchestrator's ledger. Carry: O1

## Evidence

- Round: this is the third review round, after b63d67cc and 8a05961b. From the fourth, fixer.md owes a re-cut. Head measured: a55158085ed8cd6517113af8b77af07492a6634e (ev/HEAD.txt).
- Scope: delta. The two-dot `git diff 8a05961b a5515808` includes main's own commits, because the branch merged origin/main. The authored delta is the single commit 2fb2c7f0, which touches tools/audit/seat/beat_jobs.py, beat_jobs_selftest.py and instruments/beat_jobs.py.md, plus the merge a5515808. There is no custom_components/ change, so the review does not widen. The packet's `Review scope: full` line comes from the verdict/<pr> lookup missing the probe/revt-* verdict. I read that verdict (probe/revt-r10-hotfix-macos-selftest-lane-dfbc393a, e2a81bf9) and reviewed the delta against it.
- Prior block item resolved: design-trace-missing. The body now carries the red-then-green run of the row at 19baca76 (13 RED lines, `mutant_run.py` and `prepr.sh` among them) and at 50373173 (those two are gone, 10 lines left), with wall times. These ran on an Apple M1, and this Linux seat could not re-measure them. Checked for internal consistency:
  - The real times match the stated UTC windows: 22:57:53 to 00:18:24 is 80m31s against `real 80m30.649s`, and 00:18:49 to 02:07:37 is 108m48s against 108m47.673s.
  - 6527.7 - 779 = 5748.7 s, matching 5749. The slot return at 00:31:48Z is 779 s after the 00:18:49Z start.
  - The sampled sum of 5746 s is consistent with 5749 s.
  - The eight largest runs sum to 4702 s, which leaves about 1047 s for the rest, consistent with "under 200 s each".
  - Half of 5749 is about 2875 s, matching "about 2900". 900 + 1104 = 2004 < 3600. 3600 - 900 = 2700. The 3000 s per-run bound is `timeout=3000` at beat_jobs.py:189.
  - The 13 - 3 = 10 digest lines are consistent.
  - Re-derived here: the enumerator gives 80 at 19baca76 and 81 at 50373173, using the body's own command on a `git archive` of each tip (ev/enumerator.txt).
  - Not re-derivable here: the per-run seconds, the M1 wall times, the slot wait and the RED/GREEN digests themselves. The body says its logs are machine-local.
- The `-I` defect reproduces on Linux as well, with Python 3.14.7 on the 50373173 tree. `python3 -I tools/audit/seat/queue_pre_flight.py --self-test` gives rc=1 with `ModuleNotFoundError: No module named 'merge_train'`. Plain `python3` gives rc=0 with `53 checks, 0 failed` (ev/qpf-linux.txt). So this is not a Darwin artifact, and the fix is right.
- The self-test at the head gives rc=0 with `beat_jobs self-test: 238 checks, 0 failed`, as the body claims, and all 15 darwin_* in-file mutants are killed by their named case (ev/selftest.txt, 46 s wall on Linux).
- Failing test first reproduces exactly: with the head's selftest and 8a05961b's beat_jobs.py, rc=1 and `139 checks, 5 failed`, the same five cases (ev/failing-first.txt).
- My mutants (ev/mutants.txt):
  - Killed: done_carried_to_next_cycle, complete_default_false and no_final_remember.
  - Surviving, and the block: red_carried_to_next_cycle and no_per_run_remember.
  - Surviving, out of scope (Findings): no_stale_wt_remove.
  - Surviving, but equivalent under the fixture's 600 s steps: budget_gt (`>=` changed to `>` at exactly 900 s elapsed). This is a boundary choice with no behavioural claim, so it is dismissed.
  The worktree was clean afterwards (ev/wt-status-after.txt is empty).
- Verified in code: Ctx gives `clock = time.monotonic` in production (beat_jobs.py:214). A cycle in progress resumes its own tip when main moves. A slot-take or worktree failure leaves the memory untouched.
- Merge with main: `git merge-tree --write-tree origin/main a5515808` exits 0 with tree b484d93a, so it merges cleanly (ev/merge-tree.txt).
- CI: `merge_train.py classify` was WAIT for every poll (ev/classify.log, last line quoted there). This verdict blocks on its own findings, so CI does not decide it. Red checks: none answered. The owed-reds set is in ev/owed-reds.txt.
