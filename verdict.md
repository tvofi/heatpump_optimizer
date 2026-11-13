Fix review: merge 707de42600e2431aed00ef0f6d3bb185c096ad7f

bus-nonce: c50d8e3ad373f819cfa4cccef88f2b71
pending-ci: gate

Round 3 of this hotfix (round 1 blocked `4b91c2f9f705b76db9e041e1c88ad12bb79147f8` class-open, round 2 blocked `19c3f4f85cad138f99c63309ac1717ae8d601439` class-open). Scope: delta (review packet `## Review scope`). The branch's own commits are `16de9521`, `7ed2be3e`, `8521f19b` and `6858634d`, touching `tools/audit/seat/pr_args.sh`, `instruments/open_pr.sh.md` and the mutant spec. The rest of `git diff 19c3f4f8 707de426` comes in through main merges. The range has no `custom_components/` delta, so nothing was widened. Reviewed from a detached worktree at the head.

## Findings

none

## Evidence

- Round-2 block 1 (one shared scratch tree): resolved. `pr_step_sig` now runs each measurement in its own `mktemp -d "$3/tree.XXXXXX"` directory (ret:sigpriv). A run whose tree is gone or off its sha when the self-test returns does not count as a measurement (ret:sigwhole), and neither does a run a signal ended (ret:sigkilled). Main's answer is written to `$4.tmp.$$` and renamed into place only from a whole run. The overlap arm the block asked for exists: mutant `shared` puts the blocked head's single tree back and fails on its own arm ("the host refusal whose tree the other run replaced is called the head's (#3508's defect)"). The arm prints ok at the head, so the mutant is detected (`ev/head-new-arms.txt`).
- Round-2 block 2 (surviving mutant m8, the copy-path line): resolved. The line is now tagged `mut:sigold`, and the arm "a head holding the self-test only at tools/audit/prepr.sh ... mutant mut:sigold (its line deleted) finds no self-test, so the head's" prints ok at the head.
- RESULT suite at head: `bash tools/audit/seat/pr_args.sh --self-test` gives 243 checks, 0 failed, rc 0, 5m19s (`ev/selftest-head.log`).
- RESULT reviewer mutants, each in its own worktree at the head (diffs in `ev/mutants-diff.log`):
  - m1 deletes the `ret:sigwhole` line: killed, 2 failed (`ev/selftest-m1.log`).
  - m2 deletes the `ret:sigkilled` line: killed, 1 failed (`ev/selftest-m2.log`).
  - m4 drops `rm -rf "$w"` on a failed `worktree add`: killed, 1 failed, the "directory made for one is removed" arm (`ev/selftest-m4.log`).
- Body figures:
  - The spec `dev/audit/harnesses/r10_hotfix_openpr_host_refusal_mutants.json` holds 34 mutants, S01-S21, H01-H09 and O01-O04, as the body states.
  - The body's `## Head` names `707de42600e2431aed00ef0f6d3bb185c096ad7f`, which equals the PR head (`ev/pr-body.txt`). `refs/heads/fix/r10-hotfix-openpr-host-refusal` points at it (`ev/refs.txt`).
  - The full `mutant_run.py` pass (SURVIVED NULL / KILLED per slice), the null-control count (seven arms) and the real-tree overlap timings are the fixer's. They were not re-run here, so they are not re-derived. My own mutants above and the in-suite `shared` arm stand in for them.
  - The two `Not pinned, by disposition` items (`.tmp.$$` and the `-le 128` bound) were read and accepted. Neither changes a verdict at the grain any arm can reach.
- Merge: `git merge-tree --write-tree origin/main 707de426` exits 0 against origin/main `f44e761c19dc07fff222bbd6a323bdc847ea9f04` (`ev/merge-tree.log`).
- Role contract diff merge-base...origin/main under `dev/governance/roles/` is empty.
- Cheap checks at the head (`ev/cheap-checks.log`):
  - `closure.py select` prints `MODE: SCOPED -- 1 script(s) run`.
  - `tests/structure.py` prints STRUCTURE RATCHET PASSED.
  - `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py` prints `ALL 2709 ENTITY CHECKS PASSED`, rc 0 (`ev/entities.log`). Its inner `FAIL` lines are negative-control arms.
- `VERSION`, notes heading, `custom_components/` and goldens are unchanged in merge-base...head, and no claim file is touched.
- Red checks: the body says none. `tests / nightly-status` is red at the head, but it is outside the set `merge_train.py owed-reds` prints, so it is neither owed nor a block. The earlier `gate` failure (run started 23:11Z) was re-run, and classify decides it (CI line below).
- The finding still has no committed finder's harness. The body discloses this, and the in-suite overlap arms stand in for the round-2 reviewer's probe.
- CI: `merge_train.py classify 707de42600e2431aed00ef0f6d3bb185c096ad7f --pr 3515` printed `WAIT 707de42600e2431aed00ef0f6d3bb185c096ad7f pending: gate red: none` on every poll from 23:40Z to 00:10:38Z, more than 60 s apart. The `gate` re-run (check run 131577346761) was still queued, hence `pending-ci: gate`.
