Fix review: merge 50a78a49ba19061c5d4e6e4a8f5efae62da64aab

bus-nonce: 385abebfe18f8ab993b49cda110b9520

## Evidence
- Finder's harness replayed at head (`replay`): `reruns=86 max_attempt=44 sim_minutes=72 alarm=yes`, matching the record. The same harness gave `reruns=86 max_attempt=44` with `--ci` at `52f9fc5b34` and `reruns=0 max_attempt=1` at `52f9fc5b34^`.
- Perturbation: `--no-restamp` gives `reruns=1 max_attempt=2 alarm=no`. A candidate copy whose arm 1 skips `conclusion == "skipped"` also gives `reruns=1 max_attempt=2`. The replay moves with its input, and the record's table reproduces row by row.
- Root-cause.md elements are all present: a named cause, process state (c) with its evidence, a cost test with numbers, countermeasure A carried to the fixer and B proposed with a recorded cost test.
- The census figures (1618/428 re-attempts and similar) need a saved GitHub runs TSV that I could not re-derive here. They are as reported in the record. The harness's `census` arm runs, but only on an empty input.
- Three-dot diff: 6 files (the RCA record, the harness and its JSON fixture, `bugclasses.json`, `closures.json`, `delivery/3329.md`). The delivery row is present. `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched.
- Closure classification: the harness is listed in `closures.json`. The `tests/closures`, `closure-scope` and `coverage` checks are green.
- `git merge-tree --write-tree origin/main` is clean. The ledger files `closures.json` and `bugclasses.json` auto-resolve.
- `merge_train.py classify` at this head: GREEN, nothing pending, nothing red.
- Claims stay within what the harness measured. The record marks `P(recurrence)` as an estimate, marks `orchestrator_tick.py:1441` as not measured, and calls the candidate row a control and not a fix.
