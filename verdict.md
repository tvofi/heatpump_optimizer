Fix review: merge d0ad4a212d93b6a2fb711e0483c0ac6a97367a3d

bus-nonce: 70aefc343f178e97bb730c3829911b67

Round 2: a delta review over the reviewed head 475e001874041628b919539bfdac006ba495da37.

## Evidence

- Head reviewed: `d0ad4a212d93b6a2fb711e0483c0ac6a97367a3d` (`ev/HEAD.txt`). `refs/pull/3701/head` still pointed at it when the verdict was written, and the body's `## Head` names it.
- Delta scope: `review_carry.py 475e0018 d0ad4a21` printed FRESH-REVIEW. The branch's only new authored commit is `044d63ce5`, which changes 3 files under `tools/audit/seat/`: postmerge.py (+9), carry_fold.py (+23) and record_beat.py (+4/-1). `a17d0c2f2` merges it with an empty diff against `044d63ce5`. `d0ad4a21` is a main merge of `5e2ef89b4e` with no resolution. The delta does not touch `custom_components/`, so nothing widens the scope.
- `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract read is current.
- Prior block 1 (code-defect, a clean no-group merge owed a mark) is resolved. The stage arm now does `if not queued: continue` before the no-group raise. `queued` is empty only when `code == 0` and there are no marks. For a grouped merge, the old path called `enqueue(state_dir, [], sha)`, which writes nothing (`if new:` guards the write), so skipping it leaves grouped merges unchanged. The new row `a clean sync with no roster group owes nothing, queues nothing and opens no ledger event` passes at the head. Reviewer mutant M16 (the guard changed to `if False:`) is KILLED: 3 failed, including that row with `['main classify said', 'OWED mark: queue: no group to queue']` (`ev/mutants-out.txt`). The null control row `a refused stage with no roster group queues nothing and is owed as no-group` still passes.
- Prior block 2 (mutation-vacuous M9, M10, M11) is resolved. Each was re-run in place at the head with the file's own self-test, then restored (`ev/mutants.py`, `ev/mutants-out.txt`):
  - M9-exact, `rc, lines = leased(a.state_dir, LEASE_WAIT_S, lambda: fold(...))` changed to `rc, lines = fold(...)`: KILLED, `FAIL main folds holding the lease: a lease the drain holds refuses before any roster read`, 11 checks, 1 failed. A first, looser M9 spelling was killed by a TypeError and does not count as proof; it is kept in the same file.
  - M10, `body` dropped from the `facts` return: KILLED, `FAIL the merged body is asked of gh and returned ...`, 18 checks, 1 failed.
  - M11, `,body` dropped from the `--json` field list: KILLED, the same row, 18 checks, 1 failed.
- Prior note (stale `## Head`) is answered: the body's `## Head` now describes `d0ad4a21`, `a17d0c2f2` and `044d63ce5`.
- Self-tests at the head match every figure in the body (`ev/selftests-head.txt`): beat_jobs 291/0, postmerge 40/0, carry_fold 11/0, roster_lib 103/0, record_beat 18/0, cloud_relay 521/0.
- `git merge-tree --write-tree origin/main d0ad4a21` (origin/main `5e2ef89b4e`) exited 0 with empty stderr (`ev/merge-tree.out`, `ev/merge-tree.err`).
- The three-dot diff touches none of `VERSION`, the manifest, `RELEASE_NOTES.md` or either claim file.
- `merge_train.py classify d0ad4a21 --pr 3701` printed `GREEN d0ad4a212d93b6a2fb711e0483c0ac6a97367a3d pending: none red: none` (`ev/classify.txt`).
- `tests / nightly-status` is red in the packet's digest but is not in the `owed-reds` set (`ev/owed-reds.txt`), so it is owed no answer. The previous round's inherited `instrument-self-tests` red is green at this head.
- Figures not re-derived this round: the body's `prepr.sh` run, the gate-scope line and the Carry 8 `derive_marks` figure. Carry 8 was re-derived in round 1, and this delta does not touch `derive_marks`. The `cloud_relay` `fold_superseded` mutants were not re-run, because this delta does not touch `cloud_relay.sh`.
- Finder's harness: none named. This PR is roster carry instrument work, as in round 1.
