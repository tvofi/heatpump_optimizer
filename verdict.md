Fix review: blocked 1418e0f76c475ee2c4d9e3df36bfdf7c09c39979 findings-unresolved: the delta is only the closures repair; prior block items 3-5 (carry 0's tick flag, carry 1's start time, the writers figure) are still unanswered at this head

bus-nonce: 977a10b2d453ee93f3f5956000209a26
pending-ci: gate

## Block

This is round 3, a delta review from 02df7d11bb3b1260a5847dbfd4593d5965564741 to 1418e0f76c475ee2c4d9e3df36bfdf7c09c39979. The branch adds only two commits in that range. d87036a8f2 adds `BLOCKED.md`. af1920d50e removes it and adds `tools/audit/seat/seat_gen.py` and `seat_gen_selftest.py` to `tests/closure.py` `INERT_EXCEPT` and to the `tests/entities.py` closure in `tests/closures.json`. Everything else in the range comes from merging main (a8b07f2332, which brings #3488 and #3471). `seat_gen.py`, `pulse.py` and `beat_jobs.py` are unchanged in the range. Apart from the new `## Closures repair` and `## Red checks` sections, the body still has the same text as at 02df7d11.

The round-2 verdict at 02df7d11 blocked on items 3, 4 and 5 of the round-1 block. None of them is answered at this head:

3. Carry 0's tick flag is still not built, and the body still dismisses it by analogy: "The planted `DUPLICATE seat` case already exists in `pulse.py` (two fresh ids), so no code was added there". At this head, `git grep -n -E '\.gen|seat_gen'` finds nothing in `pulse.py` or `beat_jobs.py` (rc 1, ev/prior_items_3_4.txt). Nothing on the tick reads a `.gen` move. Build the flag, or give a measured reason why DUPLICATE covers a superseded seat whose old pass still touches the report file.
4. Carry 1 asks for the session binary's start time. The `seat_gen.py` docstring (line 17) still says the lock records "its start time". `lock` (line 105) still writes `f"{mine} {int(now)}\n"` (line 115), which is the time the lock was taken. Unlike `bump` (line 55), it still takes no flock. Record the process start time, or correct the docstring and the disposition of carry 1.
5. The `## Figures` writers line still says the `git grep` gives "exactly `run_queue`, `train_add`, `dispatch`". At the PR's current merge base, f38ac9a7c0e5, that command prints 9 lines in 5 files: `bus.sh` `dispatch()`, 5 `dispatch()` call sites in `cloud_dispatch.py`, `merge_train.py` `train_add`, `queue_pre_flight.py` `run_queue` and `roster_queue.py` `run_queue` (ev/writers_at_base.txt). The conclusion (three wired writers) holds, but the figure is not what the command prints. Restate it.

The repair brief for this round seems to have covered only the closures red. Items 3-5 need a re-cut of this branch or a body edit, as stated above.

## Findings

- Residual conflict with #3484, unchanged from round 2: `git merge-tree --write-tree` of #3484's head 93e4697879e4 against this head exits 1. The only conflict is in `dev/audit/harnesses/r10_open_driver_mutants.py` (ev/merge_tree_vs_3484.txt). It comes from two adjacent `PLANTS` edits, #3484's M-livetip/M-moved-gone and this branch's carry 8 retarget to `topic_grammar.py`. It is not a duplicate. Whichever PR lands second keeps both hunks and sets EXPECTED to mutants=24 (round 2 measured 24 survived=0 with both hunks kept). Carry: R10-HOTFIX-OPENER-UNBLOCK

## Evidence

- Setup: `cloud-setup.sh --check` printed `OK python3 is /opt/hpo/venv-ci/bin/python3`. `review_packet.py render --pr 3491 --head 1418e0f7...` rc 0 and no refusals. The packet's one advisory is required-wait: the digest reads `gate` as a failure, while classify reads WAIT.
- The closures repair is consistent at this head. Both files are listed under `closures/tests/entities.py` and `inert_reads/tests/entities.py` in `tests/closures.json`, and `closure.orphan_files()` prints `[]` (ev/closures_repair.txt). `tests/entities.py` could not run here because `homeassistant` is not installed (ModuleNotFoundError from tests/harness.py), so `tests / closures` in CI decides. A reviewer mutant that deletes the two `INERT_EXCEPT` lines still gives `orphan_files() == []` (ev/reviewer_mutants.txt). So `orphan_files()` alone does not show the edit is needed. That figure is not re-derived here, and the block does not rest on it.
- RESULT self-tests at head (ev/selftests.txt): seat_gen 23 checks, 0 failed. beat_jobs 203, 0 failed. open_driver 91, 0 failed. roster_queue 67, 0 failed. merge_train 657, 0 failed (612 at 02df7d11; main's merge added checks). Harness `r10_open_driver_mutants.py`: mutants=22 survived=0, which matches the body.
- `git merge-tree --write-tree origin/main 1418e0f7` against origin/main 6e100ef69802: rc 0, tree 376a8d9f387e, `LEDGER-MERGE: resolved tests/closures.json` (ev/merge_tree_main.txt). It does not conflict with main.
- The body's `## Head` names 1418e0f76c475ee2c4d9e3df36bfdf7c09c39979, the head reviewed.
- CI: `merge_train.py classify 1418e0f7 --pr 3491` printed `WAIT ... pending: gate red: none` (rc 3) on both polls (ev/classify.txt). The block does not depend on CI.
