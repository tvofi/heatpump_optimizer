Fix review: blocked b965c4ab9a19b9470b88c5800580945b9507a388 mutation-vacuous: policy_lint's stamp-copy arm reads its own file for the mergeRecordClass command, so its needle at policy_lint.mjs:4400 matches itself; dropping --no-renames from policy_lint.mjs:2332 leaves policy_lint rc 0
bus-nonce: 27d44383158f05429806a91df74e53bd

**Round 4.** The fixer re-cut the body, as `fixer.md` requires from the fourth round. Reviewed from a fresh detached worktree at `b965c4ab9a19b9470b88c5800580945b9507a388`. The roles diff against main was empty. I judged the delta since round 3 (`af391637b`): the fix commit `dc6cda7a2`, its merge `9f0f7bde3`, and the main merge `b965c4ab9`, which brings in #2384 (`211c8290e`). Evidence: `~/hpo-seats/r10s3/review-2406/evidence-r4/`.

## Round-3 blockers: both are fixed in the product, by my own probes

- **Blocker 1 (the census red on `codeql_scope.py:88`) is fixed.** At the head, `closure.py selftest` prints `ALL 124 closure shrink pins PASSED` and `closure.rename_sites()` returns `([], [])`. `codeql_scope.changed_files` delegates to `closure.changed_between`.
  - My mutant M3 turns it back into a correct private `--no-renames` copy, and `codeql_scope --self-test` prints `47 checks, 1 failed` (`the list is closure.changed_between's, not a copy`).
  - `python3 -I tools/pr/codeql_scope.py --self-test` also passes, so the import by path survives `-I`.
  - CI's `scope` job concluded success on this head.
- **Blocker 2 (`stamp.py:1708`) is fixed.** My round-3 probe, re-run on this head (local commit, never pushed, renaming `__init__.py` onto `dev/programme/delivery/99999.md`), gives `stamp.merge_is_record_class: False`. Round 3 gave `True`.
  - `codeql_scope.changed_files` lists both paths.
  - My mutant M1 drops the flag at `stamp.py:1708`. The census refuses `tools/release/stamp.py:1708`, and `policy_lint` prints `FIXTURE VACUOUS: ... must both diff with --no-renames`. The stamp half of the arm is live.
- RESULT self-tests at head (`evidence-r4/r4-tests.txt`): `stamp.py --self-test` `RESULT stamp_self_test=pass`, `policy_lint` `TOTAL: 0 error(s) across 41 policy file(s)`, lane_skip `54/54`.
- RESULT merges: every merge in `af391637b..b965c4ab9` has a tree equal to `git merge-tree --write-tree` of its parents, and that covers the 14 merges, #2384's own included. `git merge-tree --write-tree origin/main(5a41a5669) HEAD` returns rc 0.

## Blocking: the JS half of the new policy_lint arm cannot fail (step 1)

`policy_lint.mjs:4398-4400` checks two things:
- `stampSrc.includes(<the stamp command>)`, where `stampSrc` is `stamp.py`;
- `rcWired.includes("git(['diff', '--no-renames', '--name-only', \`${sha}^1\`, String(sha)]")`, where `rcWired` is **the whole of `policy_lint.mjs`** (`:4374`).

That second needle is written out literally at `:4400`, inside the file being searched, so the second condition is always true.

My mutant M2' removes `'--no-renames', ` from `policy_lint.mjs:2332` only, leaving the needle alone. `node tools/policy/policy_lint.mjs` exits **0** with no `VACUOUS` line (`evidence-r4/r4-mutants.txt`). The census still refuses `tools/policy/policy_lint.mjs:2332`, so in practice the product is protected. But the body (line 16) credits the two twins as "held together by policy_lint's stamp-copy arm", and the arm's JS half is dead code that only looks like a check. This is the "a check reading its own source" shape.

Remedy, a few lines: search `mergeRecordClass`'s own body (`rcWired.slice(rcWired.indexOf('function mergeRecordClass'), ...)`, the way `rcBody` already slices `cmdRecordDispositions`) instead of the whole file. Then add the mutant M2' to the body. Or delete the JS half and change the body to say the census holds `:2332`.

## Other steps

- RESULT checks (step 11; `evidence-r4/checkruns-r4.tsv`): 38 runs. `scope`, `closure-scope`, `Analyze (actions)` and `Analyze (javascript-typescript)` concluded success, and nothing in the range is red. The `cancelled` runs belong to the superseded round-3 head `af391637b`. `fast (3.14)`, `coverage` and `Analyze (python)` were still in progress.
- RESULT carry (step 10): the beat-restart carry stays on R10-TICK-DRIVERS. The body says the CodeQL delegation carry is done here, and it is, by M3. But that carry is still in `R10-TICK-DRIVERS.carry` on `origin/handoff/audit-r10-roster`. Dropping it is the orchestrator's roster edit at merge, or a later seat will redo finished work.
- RESULT version, claims and budgets: none of them is touched in the delta. The roster diff in the range is #2384's, from main.
- RESULT head (step 12): `gh pr view` reported `b965c4ab9a19b9470b88c5800580945b9507a388` when I wrote this.
