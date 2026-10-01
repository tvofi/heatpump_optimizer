Fix review: merge b7ea3bd28c718b6844575c70ec1d234cc90e84fe

PR #1832 (R9-F10.9c stage 2, merge_group), delta review only: main 8a0ca90a merged into 283accde.

- Parents are 283accde and 8a0ca90a, so the queue entry keeps its second parent.
- `git merge-tree --write-tree 8a0ca90a 283accde` gives 0137630c. It differs from the head tree only in tests/entities.py, the one conflict.
- The resolution keeps both blocks. The stage-2 _mq_problems block (with its null control) now sits ahead of main's coverage-cache block (_cov_trust and _cov_marker), and _cc_problems is unchanged. No line starts with a conflict marker; the 5 marker strings in fixtures equal both parents' 5. py_compile passes.
- PR content is unchanged. The PR-vs-main diff touches the same 9 files as the authored diff d536fb4d..283accde. The +/- lines are identical, except for two added blank lines that separate the stage-2 block from main's block.
- tests.yml and governance.yml were also changed on main's side and merged cleanly. All 7 workflows that produce required contexts list merge_group and carry a concurrency block.
- merge_fastpath self-test: 25 checks, 0 failed. codeowners_gap output is identical to main 8a0ca90a, so no new uncovered files.
- tests/harness_headers.py is still run_always (tests/run.sh:476).
- The fast-path refusal set is unchanged and no barrier is lost.
- Not run locally: entities.py, because this container has no homeassistant. It is cited from the head's CI, and merge requires green CI on b7ea3bd2.
