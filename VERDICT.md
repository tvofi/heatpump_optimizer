Fix review: blocked d1becac2b30830c9fb20bda298056cc8577fb793 red-at-head: tests/entities.py fails 2 graders-head-copy checks at the head (fast (3.14)), and the one-literal _PT_JOB_CANON fix the body names does not clear them; with it applied, 2 other checks fail because the harness executes the step in a planted repo that has no tests/closure.py

bus-nonce: 826ac479f990c738b66ad301abf29bca

**Round 5.** This is the fifth `Fix review:` verdict on #2406. The earlier four blocked at `a7d97f55b`, `89d2b9465`, `af391637b` and `b965c4ab9`.

I reviewed from a detached worktree at `d1becac2b30830c9fb20bda298056cc8577fb793`. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` was empty, so my copy of the contract is current. The evidence is in `ev/` beside this file, and `ev/HEAD` holds the head I measured.

## Round-4 blocker: fixed, and pinned

- **The finding.** `recordDiffParity` now reads only the bodies of `mergeRecordClass` and `merge_is_record_class`.
- **M1** (`ev/mutants.txt`). I dropped `'--no-renames', ` from `policy_lint.mjs:2351`, which is `mergeRecordClass`'s real call. This is round 4's M2' and the body's MB19. `policy_lint` exits 1 with `FIXTURE VACUOUS: recordClassPaths`. Round 4's run of the same mutant exited 0, so the arm is live now.
- **M2.** I dropped the flag at `stamp.py:1708`. `policy_lint` reports `FIXTURE VACUOUS`, and `closure.rename_sites()` names `tools/release/stamp.py:1708`. This matches the body's MB15.
- **M3**, my own mutant. I dropped `--no-renames` from the producer at `tests/closure.py:2758`. The results:
  - closure selftest: `3 of 124 ... FAILED` (both sides, the 0-script scope, the census);
  - lane_skip: `51/54` (the three `runs on a rename` pins);
  - codeql_scope: `47 checks, 2 failed`.
  - So the producer pins are not vacuous.

## Body figures re-taken at this head

The body took its figures at `a9a26cc41`. The tree differs from this head only by main's `c8cc75ea9` content. Results are in `ev/selftests-head.txt`, and each matches the body:

| check | result at the head |
|---|---|
| closure selftest | `ALL 124 closure shrink pins PASSED` |
| lane_skip | `54/54` |
| codeql_scope `-I` | `47 checks, 0 failed` |
| roster_lib | `18/0` |
| orchestrator_tick | `104/0` |
| state_docs | all passed |
| stamp | `RESULT stamp_self_test=pass` |
| policy_lint | `TOTAL: 0 error(s) across 41 policy file(s)`, `FIXTURE ok`, no VACUOUS |
| structure | `STRUCTURE RATCHET PASSED` |

## Blocking: the head is red on its own pin, and the remedy the body names does not close it

The body's `## Red checks` says `fast (3.14)` is this PR's and still red at the head. It leaves the fix to the orchestrator and calls it "the one-line canonical literal in `_PT_JOB_CANON`".

I re-measured both halves of that claim. Each run is `PYTHONPATH=tests/hastub python3 tests/entities.py` on Python 3.14.7.

- **At the head** (`ev/entities-head.txt`): `3 of 2347 ENTITY CHECKS FAILED`. The three failures are:
  - `every pinned grader given a token runs its own copy ...` (`arm mismatch=graders-head-copy.steps[2].run`);
  - `and any edit to the arm's job ... disarms it (null control)`;
  - the `delivery_status` step-case row.
- **Null control at the merge base `c8cc75ea9`** (`ev/entities-base-c8cc75ea9.txt`): `1 of 2347`. The only failure is the `delivery_status` step-case row, so that row fails on this box regardless of the PR. The two `graders-head-copy` failures are this PR's, which agrees with the body.
- **The body's remedy, applied locally and never pushed** (`ev/canon-probe.diff`, `ev/entities-head-canonprobe.txt`): I changed `tests/entities.py:26601` to `python tests/closure.py changed --base "$BASE" --head "$HEAD"`. The result is still `3 of 2347 FAILED`.
  - The arm-mismatch pair now passes.
  - Two new checks fail: `and the arm's trigger fires on a restored path and only there` (`planted diff -> governance: {... 'outputs=[]' ...}`) and `and a trigger whose firing branch writes false is refused (null control)`.
  - The harness executes the step's script in a planted throwaway repo. That repo has no `tests/closure.py`, so under `set -euo pipefail` the new first line exits before any output is written.

So the fix is not one line. The planted repo that `entities.py` builds for the trigger check must carry, or stub, `tests/closure.py changed` alongside the canon literal. The alternative is for the step to keep a self-contained `git diff --no-renames --name-only`. The census allows that and the harness can execute it.

I did not post the `fast (3.14)` conclusion from CI because it was still `in_progress` when I wrote this (job 117746495595). My local run reproduces the failure the body itself predicts. Step 11's red-check answer is present in the body. This block is on the product being red, not on an unanswered trigger. The body's `## Red checks` remedy and its `## Friction` line should be corrected with the finding above.

## Other steps

- **Merges** (`ev/merges.txt`): `a9a26cc41`, `26962be40` and `d1becac2b` each have a tree equal to `git merge-tree --write-tree` of their parents, so none was resolved by hand. `git merge-tree --write-tree origin/main(106af95a3) d1becac2b` returns rc 0, and `LEDGER-MERGE: resolved tests/closures.json` appears on stderr (`ev/merge-tree.txt`).
- **Checks** (step 11, from the check-runs API on this head):
  - 38 runs, with no `failure` yet.
  - `fast (3.14)` and `closures` are `in_progress`.
  - `typing`, `browser`, `coverage`, `scope`, `closure-scope`, `graders-head-copy`, `pr-contract` and the three CodeQL analyses concluded success.
- **Version** (step 5): `VERSION`, the manifest and the `RELEASE_NOTES.md` heading are not in the diff.
- **Claims and budgets** (steps 4, 14): neither claim file nor any golden fixture is in the diff. `tests/closures.json` moved only through the bot's `ci: re-record closures` commit (`f95578604`), which `closures-autofix` produced from the measured `UNDER-SCOPED` read.
- **Forward-carry** (step 10): the beat restart is still on `R10-TICK-DRIVERS`, as round 4 found. The CodeQL-delegation carry is done in this PR, and the orchestrator still has to drop it from the roster at merge.
- **Head** (steps 7, 12): `refs/pull/2406/head` is `d1becac2b30830c9fb20bda298056cc8577fb793` when I write this. That is the head named in the body's `## Head`.
- **Rounds:** this is the fifth. Under `fixer.md`, a repair this late owes a re-cut. The product half (rename-safe lists, Level 0, the parity arm) holds by M1 to M3. What remains is the `entities.py` pin.
