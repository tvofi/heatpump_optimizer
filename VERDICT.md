Fix review: merge 4eed14bd8a6b0691235d2c9ce601aba465c93a1d

bus-nonce: b73b5f39ce7fe45d0c7e46c26cb74ef2

Resolution-delta review of PR #2605 (R10-NIGHTLY-PYSPY-RETRY) at head `4eed14bd8a6b0691235d2c9ce601aba465c93a1d`. The round-2 verdict was `merge 5a3c5d2395043b7ce9f82b383be350356c9d5864`. This round does not re-review the fix.

## Findings

None. The round-2 findings 1, 2 and 5 are answered; findings 3 and 4 were dismissed there and nothing here changes them.

## Evidence

- Head: `ev/HEAD.txt` = `4eed14bd8a6b0691235d2c9ce601aba465c93a1d`; the live PR head read from the REST API is the same (`ev/pr-head-live.txt`).
- Check 1, no foreign commits: `git log --no-merges 5a3c5d239..4eed14bd8a6b0691235d2c9ce601aba465c93a1d ^origin/main` prints nothing. The only merges in the range are the base merge `4eed14bd8` and main's own #2608 merges.
- Check 2, delta is main's own change: `git merge-tree --write-tree 5a3c5d239 origin/main` yields tree `7e5048d0dd420ceeafcc9a3f385d4ddfef84e008`, which equals the head's tree, so the merge has no conflict resolution (`ev/merge-recompute.txt`). The delta `5a3c5d239..head` touches only `dev/programme/delivery/2608.md` and `dev/programme/rosters/wave-r10-groups.json` (`ev/delta-stat.txt`); no code, test or version file moved.
- Check 3, body: `ev/body-diff.txt` compares the round-2 body copy with the live body. Only three hunks differ: the two `## Head` paragraphs (the stale `e0725a9ede5b` paragraph is gone, the head is named correctly) and `## Red checks`, which now names `pr-contract` (BAD-DEST, resolved by #2608 plus this base merge) and `nightly-status`, each with cause, cheaper detector and a Carry line. Every other section is byte-identical.
- Check 4, carry: `carry_audit.py check --body` at this head prints `3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)` (`ev/carry-audit-body.txt`). `pr-contract` at this head: both runs completed `success` (12:11:56Z and 12:12:24Z, `ev/check-runs.tsv`). `nightly-status` is completed `failure`; it is not a required context and does not block. `closures`, `coverage`, `fast (3.14)`, `Analyze (python)` and `instrument-self-tests` were still running when read; that is not a block.
- Check 5, pinned tests, with a limit I could not lift. The full `tests/entities.py` did not run on this seat: venv-ci has no homeassistant, and venv-ha (homeassistant 2026.9.3) fails in `harness.py` with `AttributeError: 'FakeConfig' object has no attribute 'config_dir'`. Origin/main fails identically in the same environment (`ev/entities-main-env.txt`), so the failure is the seat's HA version and not this PR. `tests/nightly_ha.py` needs docker, absent here (`ev/nightly_ha.txt`). What I did run is the round-2 null driver against the real `_async_hb_control` at production defaults on the merged tree (`ev/null-control-head.txt`): never-answers `pass=False calls=3 elapsed=17.9s`; answers-without-spin `pass=False calls=3`; rc1-only `pass=False calls=3`; hang-hang-spin `pass=True calls=3`, rc=0. All match round 2. Beyond that, the claim that the full suite and the mutant table (14 killed, 0 survived) hold rests on the code and tests being unchanged between the round-2 head and this one (check 2) and on round 2's recorded runs; CI on this head has not yet finished its test jobs.
- Check 6, merge: `git merge-tree --write-tree origin/main 4eed14bd8a6b0691235d2c9ce601aba465c93a1d` exits 0, tree `7e5048d0…` (`ev/merge-tree-main.txt`). The head contains origin/main `543c8087c`.
- No /Users/ or /private/ path appears in this verdict or in `ev/`.
