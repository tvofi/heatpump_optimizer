Fix review: merge 56123c47dfab59a335f987510588b7e7bcff0783

bus-nonce: fa98879c941fc475b0b24c143cfee9a3
pending-ci: gate

Round 2, a delta review over the reviewed head d339e84355. The scope is `git diff d339e84355 56123c47df`, which is the same two files as `git diff d339e84355 eef6a631a7`: tools/ci/sweep.py and tools/ci/sweep_selftest.py. The merge commit adds nothing else. The delta touches no `custom_components/` code, so the scope is not widened.

## Prior block

- Resolved. The previous block was `class-open`: code_red counted units whose grader the stale pin restores. At this head `code_red` drops any `REQUIRED["no-pr"]` name that starts with a `pinned_graders()` prefix, and that set is read from `.github/workflows`. On the tree it returns `tests / briefs`, `governance / policy-docs`, `governance / env-matrix`, `governance / wave-script` and `codeql / Analyze (` among its prefixes (`ev/pinned-enumeration.txt`). These are the five kinds the block named.
- The axis is closed for the set that code_red reads. I asked a separate locator to check every other `REQUIRED["no-pr"]` job for a restore from `github.event.pull_request.base.sha` under a variable other than `PINNED`. The jobs checked were fast, arch-instrument, browser, typing, mutation, closure-scope, closures, hassfest and validate-hacs. None restores a program from base.sha. closure-scope (tests.yml:1970) and closures (tests.yml:2182) use `BASE` only as a diff range for the head's own `closure.py`.
- The one restore outside the rule is `mutation-pins` (tests.yml:1282/1316, `git show "$PR_BASE":tests/mutation_table.py`). It is not in `REQUIRED["no-pr"]`, so code_red never reads it.
- The reviewer's two null cases (`tests / briefs` red, `governance / policy-docs` red) are now cases in the head's own loop, together with env-matrix, wave-script and codeql python. All of them pass.
- In the tree replay, dispatch 45005979443 now reads `dispatched` (`ev/stalepin-wt-2026-11-22.txt`).
- Prior finding M6/M7 is resolved: both mutants are now killed (below).
- Prior note on the 17 -> 16 figure is resolved: the module doc and the docstring both say 16.

## Findings

- Surviving mutant at this head: in `pinned_graders`, dropping `and name is None` from the `    name:` branch leaves `123 checks, 0 failed`. On the tree's own workflows it is equivalent: the output is byte-equal with and without the guard (`ev/mutant-F-equivalence.txt`), because no job block carries a second 4-space `name:`. No fixture pins the first-name-wins rule. A fixture job with two `    name:` lines would kill it. This is not a block: the claim's behaviour on the tree does not depend on the guard. Carry: #3885

## Evidence

- RESULT: `python3 tools/ci/sweep.py --self-test` at 56123c47df prints `sweep self-test: 123 checks, 0 failed`. Carry: dismissed: evidence, not a finding
- RESULT: mutation proof, re-run by me (`ev/mutants.py`, `ev/mutants.txt`). 15 of 16 mutants are killed. Pinned exemption off: 5 failed (one per pinned kind). Fail-open on unreadable workflows: 1. PIN_MARK test dropped: 1 (the fixture's github.sha null). No split at the first expression: 3. Key in place of name: 3. Any indented key read as a job: 6. pinned_graders returning None: 5, and returning (): 7. M6 (status ignored): 1. M7 (key order swapped): 1. M2 `!= "success"`: 1. M3 first-wins: 1. code_red returning []: 3. PIN_MARK set to github.sha: 3. in_jobs never set: 7. Unmutated after restore: 123 checks, 0 failed. The fixer's R6-R12 counts match these where the mutants coincide. Carry: dismissed: evidence, not a finding
- RESULT: re-measurement with the head's `ci3885_light.py stalepin` arm, from detached worktrees at the head and at origin/main d3d66c4040 (`ev/stalepin.txt`, `ev/stalepin-*-2026-11-22.txt`).
  - 11-23 head: `leaves 2 (304 runner-min) and still dispatches 0 (0)`. 11-23 main: `leaves 0 ... dispatches 2 (304)`.
  - 11-25 head: `leaves 3 (1038 runner-min) and still dispatches 1 (421)`. 11-25 main: `leaves 0 ... dispatches 4 (1460)`.
  - 11-22: my 900 s timeout cut both runs before the summary line, after 17 of 21 duplicates. The remaining duplicates (44993171735, and 44970786457 at main) read `unattributed` in the first pass. Summing the per-run lines at the head gives left 8 (2498 runner-min) and dispatched 6 (3724; the body says 3725, a per-run rounding difference). At main all 14 attributed runs read `dispatched`.
  - All of this re-derives the body's 13 of 20 left, 3,840 runner-min (2498+304+1038). Carry: dismissed: evidence, not a finding
- RESULT: local harness adaptation, disclosed. This seat's gh 2.89.0 rejects `--allow-escape-sequences`, so I removed the flag in the two worktree copies only (`ev/harness-local-patch.diff`). Nothing was pushed. The body already carries this gap to #3885. Carry: dismissed: evidence, not a finding
- RESULT: `git merge-tree --write-tree origin/main 56123c47df` exits 0 (tree a84aecf331), with no conflict. The delta does not touch VERSION, the manifest, RELEASE_NOTES.md, claim files or golden fixtures. Carry: dismissed: evidence, not a finding
- RESULT: CI. `merge_train.py classify 56123c47df --pr 3895` printed `WAIT ... pending: gate red: none` on every poll from 13:48 to 14:38Z (`ev/classify.log`). That is past the 30 min bound, so the verdict carries `pending-ci:`. No check is red, so no red is owed an answer. Carry: dismissed: evidence, not a finding
- RESULT: the head's body names 56123c47df and the delta d339e84355..eef6a631a7. Both match what I measured. Carry: dismissed: evidence, not a finding
