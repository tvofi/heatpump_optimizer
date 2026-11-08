Fix review: merge b7c7c9c5671dce74fe4d048a7a1ae2502e742efd

bus-nonce: bc8c6a6f1621e4dd17ec1addb76fffe8

Round 1 (sonnet). The diff has two files: a four-line paragraph in `tools/audit/seat/instruments/tick_loop.sh.md` and the delivery row `dev/programme/delivery/3340.md`.

## Evidence
- The paragraph's claim holds at the head. `RELAY_HOLDER` in `tools/audit/seat/tick_loop.sh` calls `os.setpgid(0, 0)` (line 65). The holder writes `<out>.relay.rc` under its flock (lines 60-64).
- The self-test pins it. The row "a TERM to the loop's process group leaves the in-flight relay to write its rc" is at lines 224-230.
- RESULT, base: `tick_loop.sh --self-test` gives 27 checks, 0 failed (`ev/selftest-base.txt`).
- RESULT, mutant: with the `os.setpgid(0, 0)` line deleted, the self-test gives 27 checks, 1 failed (`ev/selftest-mutant.txt`). The self-test was restored afterwards and the tree is clean.
- The diff touches no production line, so no mutants are owed on it.
- The delivery row `dev/programme/delivery/3340.md` is in the diff.
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched.
- `git merge-tree --write-tree origin/main HEAD` exits 0, with no conflict.
- `merge_train.py classify` prints GREEN, rc=0: pending none, red none. The PR ref head equals the reviewed head.
- Architecture: `archscore --diff` gives dS +0.0000 NULL. This is a doc-only diff, no structure budget is raised, and no new file is tracked.
- `tests/entities.py` did not run clean: it died with `ModuleNotFoundError: No module named 'homeassistant'` in `tests/harness.py`. This is an environment gap in the cloud seat, not a finding on the PR. The diff adds no new tracked file apart from the delivery row, which is a delivery-record path.
- I did not read the PR body through the API (rate-limit discipline). The PR body's `## Head` and `## Red checks` were not checked. The packet's gate digest shows no red check and no refusal.

## Findings
(none)
