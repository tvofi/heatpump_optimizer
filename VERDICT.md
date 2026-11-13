Fix review: merge fb91a335519d240eacdcd8ccfdb8fa4a64058463

bus-nonce: 777cfc4923127b1a69c583f117ad33be

## Scope

This is round 2 and a delta review over the reviewed head eb07df9be8dbea332c525525ab538ab3e7c60a41. The `git diff eb07df9be8 fb91a33551` delta includes `custom_components/` changes. All of them come from merging origin/main e23124ff6e, which is the merge base. `git diff --stat e23124ff6e fb91a33551` lists only the PR's four files: `tools/ci/selftest_closures.json`, `tools/ci/selftest_scope.py`, `tools/ci/selftest_scope_mutants.sh` and `dev/programme/delivery/3557.md`. The PR authored no production code, so the review does not widen (fix-review.md step 12).

## Prior findings

- The block (the table narrowed by wholesale replacement) is resolved. At the head the table answers every read that main e23124ff6e and the reviewed eb07df9be8 tables answer. The only list entries missing are throwaway-git-helper's 212 probes, and each sits under a directory the head lists (`.`), so `compact_probes` dropped them and no read is lost. All 4 flags the block named are back to True: app-push objects (git [merge-base] restored), throwaway-git-helper objects, tick-loop index and objects, and beatd index. Evidence: ev/table-superset.txt.
- The first follow-up (check --write wrote the bare measurement) is resolved. `check_cli` now writes `union_entries(table, measured)`, and the docstring describes the union.
- The second follow-up (the 33-versus-34 compaction gap) is resolved. `drift()` now excuses a probe under a directory the run listed, and that probe is still refused once as the step's `dirs` miss when the table lacks the directory, so no refused step is lost.
- The third follow-up (the body called tick-loop's flag change a refusal) is resolved. The body now describes it as the first cut's narrowing and says CI printed no flag refusal.

## Evidence

- Head reviewed: fb91a335519d240eacdcd8ccfdb8fa4a64058463, the PR's head on the REST read (ev/HEAD.txt). `git merge-tree --write-tree origin/main fb91a33551` exits 0 with no conflict (ev/merge-tree.txt).
- `python3 -I tools/ci/selftest_scope.py --self-test` at the head: `120 checks, 0 failed` (ev/selftest-head.txt).
- Mutation proof, re-run by this seat. The 4 mutants the PR adds were applied one at a time to `tools/ci/selftest_scope.py` and the self-test run after each. All 4 were KILLED at rc=1, each failing the arm the body names (ev/mutants-new.txt), and the worktree was restored clean.
- Drift replay, using the body's own command with MEASURED as the eb07df9be8 table (the CI artifact): 154dbb4c61 33, e23124ff6e 33, eb07df9be8 0, fb91a33551 0. That matches the body's "vs CI artifact" column. `selftest_scope.py static` gives `114 gated step(s), 0 problem(s)` (ev/drift-replay.txt).
- Not verified: the "Linux strace record at head" column of the body (36 / 36 / 13 / 0) and the `8 refusal(s)` -> `0 refusal(s)` check over the seat's traces. A full `record` does not fit this seat's window, as the previous round also found. I did not re-derive these figures.
- `VERSION`, the manifest version and the RELEASE_NOTES.md heading are untouched, because the diff from main is the four files above.
- No finder's harness is named. That fits a hotfix of an instrument and its measured table.
- CI: `merge_train.py classify fb91a335519d240eacdcd8ccfdb8fa4a64058463 --pr 3557` printed `GREEN fb91a335519d240eacdcd8ccfdb8fa4a64058463 pending: none red: none` (ev/classify.log). No owed red, so no `## Red checks` answer is due.
- Round: 2.
