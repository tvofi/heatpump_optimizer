Fix review: merge 720220f19e40aeacf59fac0b8c9ca58221275c97

bus-nonce: 7a45f5c736bdbfa53760724edb95ea1a

## Scope

Fix review of PR #3280 (R10-FLY-STAMP-FLUSH-HOLD) at head 720220f19e40aeacf59fac0b8c9ca58221275c97. The head merges code head 60b97bb5d872 onto origin/main a37c58e5f. This review covers repair round 2; the previous verdict blocked d65bcee9bdfb, so this is not the fourth round. It was run from a detached worktree at the head and checked by the three-dot diff from merge base a37c58e5f32123b4028e90983799dc2aa81816f8: 3 files, +265/-14. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.

## Evidence

- RESULT merge_train_self_test: `merge_train self-test: 472 checks, 0 failed`, rc=0 (ev/merge_train_selftest.txt). This matches the body's 472.
- RESULT stamp_self_test: `RESULT stamp_self_test=pass`, rc=0 (ev/stamp_selftest.txt).
- RESULT structure: `STRUCTURE RATCHET PASSED`, rc=0 (ev/structure.txt). No `*_budgets.json` file is in the diff.
- `bash tools/pr/prepr.sh` rc=0 was not re-run here, because it is a heavy lane (fix-review 11). CI's code run 42387117401 stands in for it: its gate is green.
- Mutation proof (ev/mutants.txt). Each mutant was applied to the real file in a scratch worktree and the self-test re-run:
  - Null control: the file was left unmutated, because the null's replacement string was not unique. Both self-tests pass.
  - M1 `mut:stopign` (handler = SIG_IGN): rc=1, killed by `FAIL a first TERM in batch 1's closing release stops the train: no second batch, exit 143`.
  - M2 `unwind` without `stop_ignored` (nullcontext): rc=1, 4 FAIL, including `a train TERMed again during its unwind still deletes the hold ref`.
  - M4 `mut:deferdeliver` → pass: rc=1, killed by the same batch arm as M1.
  - S1 `not hold` removed at the first dispatch: rc=1, killed by `flush: a planted live hold is named, announced once, and spends no dispatch` and by the predicate-mutant arm.
  - S2 `not hold` removed at the re-dispatch: rc=1, killed by the same two checks as S1.
  - S3 give-back (`count - 1`) removed: rc=1, killed by `flush: a dispatch sent before the hold appeared is taken back ...`.
  - S4 future-dated hold read as young (`0 <=` dropped): rc=1, killed by the `hold:` arm.
  - S5 bound replaced by literal 3600: rc=1, killed by `hold: the bound is nightly.yml's own HOLD_MAX_AGE_S by source read`.
  - S6 initial `held()` ignored: rc=1, killed by the planted-live-hold arm.
  - M3 `stopping = False`: survives. See Findings.
- The in-tree mutants `mut:stopign`, `mut:deferdeliver` and the record_flush predicate mutant run inside the self-test and report `ok`. Each has a null control that passes: the no-signal batch run, the one-TERM train run, and the absent-hold flush.
- Bound by source: `.github/workflows/nightly.yml:1064` has `HOLD_MAX_AGE_S=3600`. `hold_bound_s` parses that line, and `3600` is absent from `train_hold`/`hold_bound_s`. The staleness rule matches nightly.yml:1080-1087: age < 0 is stale, age >= bound is stale, and an unreadable read is treated as absent. A held beat exits `skip-train-hold` before the step `Approve and merge a row-only record pull request` (nightly.yml:978). That is the record merge the flush waits for, so the premise holds.
- The hold commit message carries `train hold pid=<pid>` (merge_train.py:2446), which `train_hold` parses.
- Class rule: `grep -n "stop_ignored\|\.unwind()"` returns lines 315, 2490, 2498 and 3222 (ev/class_rule.txt). The other `hold_release()` sites are 2511, 2515, 3554 and 3568. All four run inside `_train`/`_batch`, whose callers `train`/`batch` end in a `finally` that calls `unwind()`. A stop that cuts one short therefore still reaches the guarded DELETE. The class is closed.
- `git merge-tree --write-tree origin/main 720220f` (origin/main 1c1ae100b59e) exits 0 with tree 86ee10ba425b; there are no conflicts (ev/merge_tree.txt).
- VERSION, the manifest and RELEASE_NOTES.md are not in the diff. The delivery row dev/programme/delivery/3280.md is in the diff. The tracked-file classification is pinned by CI's green gate (tests/entities.py runs in it).
- `## Head` names 720220f19e40aeacf59fac0b8c9ca58221275c97, which is the head measured here. refs/pull/3280/head was still 720220f at verdict time.
- Closes line: commit cd88cf6bd00d holds dev/programme/triage/s6-batch131.md. Its `## P402: stamp-flush-train-hold-deadlock` section is ACCEPT narrowed and names this group, so the Closes line is confirmed.
- CI at this head:
  - Code run 42387117401: `gate` check 128458902391 concluded success at 16:27:27Z. `pr-contract / pr-contract` 128458457723 concluded success; it started at 16:24:22Z, after the last red.
  - Edit run 42387746876: `gate` 128451094829 failed with `FAIL run(s) [42387117401] at this head are still being judged; their gate decides`. That is an edit-run deferral, and the code run has since decided it green.
  - Run 42386973728: gate, arch-score and budget-raise-gate were cancelled as superseded.
  - `tests / nightly-status` 128447934775 is red because main's nightly 42369836867 was cancelled. The diff does not reach nightly.yml, and the check is unrequired, so this red is not this PR's.
  - `merge_train.py classify` still prints `RED ... pending: none red: gate` (rc=1, ev/classify.txt). By A5 it keeps the edit suite's deferral red beside the code suite's green. Following the brief's gate-deferral rule, I judged the head GREEN myself.

## Findings

- Surviving mutant M3: replacing `stopping = isinstance(sys.exc_info()[1], SystemExit)` with `stopping = False` passes all 472 checks, so the drop-when-already-unwinding branch is unpinned. Under the mutant, a second TERM is re-delivered after the hold DELETE, through the restored `unwind` handler. That raises a second SystemExit of the stop code after the DELETE has gone out. The hold is still released, and only the exit code can differ (a HUP-first stop would end 143). This is near-equivalent for what the group protects. Carry: dismissed: near-equivalent mutant, the hold DELETE is issued under it and only the exit status of a doubly-signalled stop can differ
- `## Red checks` reports the check-runs of d65bcee9bdfb (`none`), not this head's. The concluded reds at 720220f are superseded cancellations, an edit-run gate deferral decided green by the code run, and main's nightly-status. None is this PR's. The trigger is answered by `pr-contract` 128458457723, which started after the last red and is green (fix-review 11: that run is the evidence). Carry: dismissed: no red at this head is this PR's and the post-red pr-contract run is green

## Friction

- The frugal inline-search guard stopped a check of the mutant output part-way; the run was finished from the task notification instead.
