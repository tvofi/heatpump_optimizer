Fix reviewer for PR #2666, R10-FLY-INERT-LOAD-TIME (lane FLY, size S, instrument), the barrier for audit class I2, built by the root-cause seat beside #2662. Branch fix/r10-rca-inert-closure-recording, head 0dda6260a8261233bb435442e52c219f3117a747. The code head is e9d169b7; 0dda6260 adds only the delivery row. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. Your ev/ MUST contain ev/HEAD.txt holding the full 40-hex head, or the relay refuses the verdict.

Claim: a closures recording carries an inert_reads split decided by the recording tree's INERT list. A later INERT_EXCEPT edit voids that split, but `merge` and `check` trusted it, so `check` passed vacuously (#2662's probe d5b053e then went UNDER-SCOPED: 32 min of red FULL closures). The barrier:
- tests/closure.py `_load_recording` re-splits each recording's inert_reads under the loading tree's INERT list, for merge and check;
- tools/pr/ci_predict.py `left_inert` predicts UNDER-SCOPED statically when a diff edits tests/closure.py and a committed inert_reads file has left INERT while its script's closure omits it (prepr step 6d, body_push);
- the RCA doc dev/audit/rca/R10-RCA-INERT-CLOSURE-RECORDING.md and a bugclasses.json I2 entry.

Verify adversarially, with the finder's harness:
(1) Three-dot diff: only the five files above, plus fixtures/tests for them and dev/programme/delivery/2666.md.
(2) Reproduce instance 3 yourself. At d5b053e (fetch it), run `check` over the d0ff8268b-era recording (artifact 12493224545, or rebuild an equivalent fixture recording) with main's closure.py: rc 0, vacuous. Then with this PR's closure.py: rc 1, UNDER-SCOPED on u5's run_part.py and unitcheck.py under tests/harness_headers.py. `ci_predict.py` at the head predicts the same 2. Never run a full derive_closures.sh off Linux; `--single` on a Python script is allowed.
(3) Null controls: an INERT edit whose recordings are fresh passes check and predicts nothing; a recording whose inert_reads files are all still INERT is unchanged by the re-split; and the 8 live inert_reads entries the RCA says are not under-scoped today produce no false UNDER-SCOPED on main's committed closures.json.
(4) Mutants: drop the re-split in _load_recording, drop left_inert's closure-omits test, and make left_inert ignore diffs that edit tests/closure.py. Each must go red.
(5) The figures: the cost numbers (7.1 ms per recording, 8.1 ms per predictor run, 28 INERT_EXCEPT edits, 82 non-merge commits) and the process-state (c) claim. Re-derive what you can and mark the rest not re-derived under ## Evidence. Run `python3 tools/audit/fold_ledger.py check` and record its violation count.
(6) `git merge-tree --write-tree` against origin/main is clean. Read CI with one bulk check-runs call. No commit carries a footer. Record the scoped-gate MODE line.
Rules: PREPR_SKIP_CLOSURES=1; spare the GitHub API; no Claude footers.
