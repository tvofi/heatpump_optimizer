Fix review: blocked 02df7d11bb3b1260a5847dbfd4593d5965564741 findings-unresolved: the scope-overlap and the carries 5-7 lines are fixed, but three items from the prior block (carry 0's tick flag, carry 1's start time, the writers figure) are still open at this head

bus-nonce: 3f645d10396e7bd2acd2390107d07740
pending-ci: gate

## Block

This is round 2, a delta review of b18d78b5070ca6fc27f8a865240e295a544c18c2..02df7d11bb3b1260a5847dbfd4593d5965564741. The branch's own commits in that range are 3e39de94d (drop carry 9), e30e995c6 (the delivery row) and two merges of main. None of them touches `custom_components/`. The production files in the range diff come from main's merges (#3454, #3460, #3473), so the scope is not widened.

The two points the repair was sent to fix are fixed (Evidence). The prior verdict blocked on five items. The repair brief named only items 1 and 2. The delta touches none of items 3-5, so each still stands and is still unanswered:

3. Carry 0's tick item is still not built and is still dismissed by analogy. The body says "The planted `DUPLICATE seat` case already exists in `pulse.py` (two fresh ids), so no code was added there". `pulse.py:248` keys on two fresh alive ids, not on a `.gen` move. Neither `pulse.py` nor `beat_jobs.py` reads `.gen` or `seat_gen` at this head (ev/prior_items_3_4.txt). Build the flag, or give a measured reason that DUPLICATE covers a superseded seat whose old pass still touches the report file. Carry: dismissed: owed by this branch's re-cut, a block item
4. Carry 1 asks for the session binary's start time, and the `seat_gen.py` docstring (line 17) still says the lock records it. `lock` (line 105) still writes `f"{mine} {int(now)}\n"` (line 115), which is the time the lock was taken. Unlike `bump` (line 55), it still writes without a flock. `seat_gen.py` is unchanged in the delta. Record the process start time, or correct the docstring and the carry 1 disposition.
5. The `## Figures` writers line still reads "exactly `run_queue`, `train_add`, `dispatch`", measured at the merge base. At the PR's current merge base 2ced371c1, that `git grep` prints 9 lines in 5 files: `bus.sh` `dispatch()`, 5 `dispatch()` call sites in `cloud_dispatch.py`, `merge_train.py` `train_add`, `queue_pre_flight.py` `run_queue` and `roster_queue.py` `run_queue` (ev/writers_at_base.txt). The conclusion (three wired writers) holds by reading, but the stated figure is not what the enumerator prints. Restate it.

## Findings

- Residual conflict with #3484, one file: `git merge-tree --write-tree 301122324b93 02df7d11bb3b` still exits 1, now only in `dev/audit/harnesses/r10_open_driver_mutants.py`. The other two files of the prior three, `open_driver.py` and `open_driver_selftest.py`, no longer conflict (ev/merge_tree_vs_3484.txt). The cause is two adjacent edits in `PLANTS`: #3484 inserts M-livetip/M-moved-gone, and this branch retargets M-exact/M-body to `topic_grammar.py` (carry 8, kept by the prior remedy). It is not a duplicate. Keeping both sides gives mutants=24 survived=0 (ev/harness_trial_merge_3484.txt). #3484's own harness, unmerged, aborts M-exact at its head, because `if up in groups` occurs 0 times in `open_driver.py` there: `resolve()` moved to `topic_grammar.py` in a7fd743e5, which is in #3484's base. So #3484 needs this retarget too. Whichever of the two lands second resolves by keeping both hunks and setting EXPECTED mutants to 24. Carry: R10-HOTFIX-OPENER-UNBLOCK

## Evidence

- Setup: `cloud-setup.sh --check` printed `OK python3 is /opt/hpo/venv-ci/bin/python3`. `role_pack.py render fix-review` rc 0. `review_packet.py render` rc 0, with no refusals and Review scope `delta`.
- Prior item 1 (scope-overlap) is resolved. The PR's own three-dot diff against merge base 2ced371c1 no longer touches `tools/audit/seat/open_driver.py` or `open_driver_selftest.py` (`git diff --quiet` rc 0). There are no `live_tip`/`RETIP` lines in `open_driver.py` from this branch. The M-livetip/M-gone-tip plants are removed, and the harness EXPECTED line is back to mutants=22. The body answers carry 9 as "owned by #3484".
- Prior item 2 is resolved. The body reads "part 1 of 1: carries 0-4, 8", and carries 5-7 are "marked `[moved: R10-HOTFIX-OPENER-UNBLOCK]` on the roster ... (open #3484), not later parts of this group".
- The repair did not otherwise move the reviewed behaviour. `git range-diff` shows the reviewed commits 1-6 unchanged (`=`). The only new commits are e30e995c6 (delivery row) and 3e39de94d (3 files, 5+/21-, all P603 removal).
- RESULT at head 02df7d11bb3b: seat_gen 23 checks 0 failed; beat_jobs 203 checks 0 failed; open_driver 91 checks 0 failed (93 before, minus the two removed live-tip checks); roster_queue 67 checks 0 failed; merge_train 612 checks 0 failed (ev/selftests.txt).
- RESULT harness `r10_open_driver_mutants.py` at head: mutants=22 survived=0. M-exact, M-body, M-crit and M-triageB are each killed (ev/harness_head.txt). This matches the body's figure.
- RESULT trial merge of #3484 head 301122324b93 into this head, with both hunks kept: mutants=24 survived=0 (ev/harness_trial_merge_3484.txt).
- `git merge-tree --write-tree origin/main 02df7d11bb3b` rc 0, tree ebed5010545c, origin/main be86e36a560f. No conflict with main (ev/merge_tree_main.txt).
- The body's `## Head` names 02df7d11bb3b1260a5847dbfd4593d5965564741, the head measured (step 7).
- CI: `merge_train.py classify 02df7d11bb3b --pr 3491` printed `WAIT ... pending: gate red: none` (rc 3) on every poll in this session (ev/classify.txt). The packet digest's earlier `gate` failure is superseded by classify. `tests / nightly-status` is red but is not in the owed-reds set (ev/owed_reds.txt), so it is not this PR's and is not answered. The block above does not depend on CI.
