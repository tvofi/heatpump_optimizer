Fix review: merge 3959ab0d511aec0166121f2cfeff742b7a833da9
bus-nonce: d11faefc832e3e5729136ab45321d15c

Round 1 (full scope, no prior reviewed head). Measured in a detached worktree at 3959ab0d511aec0166121f2cfeff742b7a833da9; roles diff vs origin/main empty; `git merge-tree --write-tree origin/main 3959ab0d511aec0166121f2cfeff742b7a833da9` exits 0.

RESULT self-tests at head: cancel_superseded 88 checks, 0 failed; merge_train 841 checks, 0 failed.
RESULT mutation (reviewer's own, evidence mutants.txt): cancel_superseded fallback deleted -> 1 failed; its endpoint back to /rerun -> 2 failed; merge_train unstale fallback deleted -> 1 failed; its endpoint back to /rerun -> 3 failed; fallback made unconditional -> 5 failed. Every mutant killed; counts match the body's.
RESULT class: `git grep -nE '/rerun([\"' )]|$)' -- tools .github tests` and `gh run rerun` re-run: every remaining whole-run POST is one of the two fallbacks or a self-test fixture; the rest are job-scoped (actions/jobs/<id>/rerun) or already `--failed` (codeql-triage-poll.sh). Class closed as the body states.
RESULT claim files, VERSION, manifest, notes heading: untouched (diff is three tools/ files plus the delivery row).
RESULT live checks at 3959ab0d511aec0166121f2cfeff742b7a833da9: only `tests / nightly-status` failure (not required); `gate` reads success on its newest check-run 140320133766 (two older gate check-runs failure, superseded).
Finder's harness: none named in the packet; the body's `ci3885_queue.py rerun` arm was applied by hand via MCP reads (builder's, not re-derived here) and its after-measurement is owed post-merge.

Note: residual-config: `Train.unstale` falls back only on a refused failed-only re-run. A stale check-run in a run that also holds a failed or cancelled job (e.g. the non-required `tests / nightly-status` red in the tests workflow) gets an accepted failed-only re-run that does not touch the stuck job, so the train now Stops on it where the whole-run re-run used to clear it. Fail-safe (a visible stop, no unsafe merge), tools-only, outside the design's named cases; not blocking.
Note: figure-unverified: the rerun-arm before figure (0 jobs, 6 of 11 runs) was not re-derived by this reviewer.
