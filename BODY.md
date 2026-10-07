The root cause of the `harness` friction key (#2004), with the defect found while re-deriving its count fixed. Since #1919 moved `policy_lint.mjs` into `tools/policy/`, the friction filer has spawned it at its old path, and the pre-flight has run it there. Every governance `record` run on `main` since then has refused at the friction step, and every pre-flight prints `policy corpus -- NOT compared`. Both now find the program where the tree keeps it. Each fix comes with a check that was committed first and shown failing.

Closes #2004. Leaves #201 open.

Analysis: `dev/audit/rca/R9-RCA-2004.md`, registered as `_rca["R9-RCA-2004"]` in `tools/audit/bugclasses.json`.

## Root cause

- **Cause:** `harness` is one verdict class covering four reviewer obligations: `class-open`, `design-trace-missing`, a carry (`since-null`), and an env-matrix base-driver run. #1881 closed the key as FIXED by step 18, which reached only the out-of-tree-harness child. Of the 7 entries (5 PRs) in this window, `class-open` is the only child at threshold (4 entries, 3 PRs).
- **State:** (c) for the key. (c) for `class-open` entries 2 to 4: `fixer.md` step 8 makes the enumeration conditional on clearing an instance block, while `fix-review.md` step 6 opens the class on every review. (b) for entry 6 (step 6's re-execute after merge) and for #1994's carry. (d) for the moved-path class.
- **Cost test** (minutes, this window):
  - Aligning step 8: about 171 min standing at an estimated 3 min per PR, against 129 min of defect. It also would not have prevented #1986 or #1993. Refused.
  - Sub-keying the histogram: recommended to D13, not built.
  - Moved paths: 6 of 6 `main` governance runs red at the friction step, the pre-flight comparison dark, and about 92 min of #1993 rounds, against a self-test `existsSync` plus about 2.4 s for one fixture arm. Built.

## Head

`64c1744dbd6ab37a53e695eaa86239cdd5f13f34`

## Mutation proof

- `tools/policy/friction_issues.mjs`:
  - The detector commit `ca9b3257` alone gives `node tools/policy/friction_issues.mjs --self-test` rc=1: `FAIL the stats tool this lane spawns and quotes is a file: .claude/workflows/policy_lint.mjs`, `100 passed, 1 failed`.
  - At the fix `ed40307b`: rc=0, `101 passed, 0 failed`.
  - Renaming the sibling to `policy_lintX.mjs` gives `FAIL ... policy_lintX.mjs`, `100 passed, 1 failed`. The rename was restored.
- `tools/audit/harnesses/r9_fr3_family_consumer.mjs` (fix-review round 1 finding, line 43):
  - At `3d31fc52` (the line reads `.claude/workflows/friction_issues.mjs`): rc=1, `ENOENT: no such file or directory, open '.../.claude/workflows/friction_issues.mjs'`.
  - At the fix `64c1744d` (the line reads `tools/policy/friction_issues.mjs`): rc=0, all family arms `ok`, including `a producer that prints the family row without counting it refuses`. Restoring the old spelling gives the rc=1 again.
- `tools/pr/preflight.sh`:
  - The detector commit `bf669af7` adds arm 5 to `tests/entities.py`'s stale-corpus fixture: the same stale head, with `policy_lint.mjs` under `tools/policy/` only.
  - The fixture, extracted and run on its own, gives at `bf669af7`: `policy corpus -- NOT compared: policy_lint.mjs here does not answer --corpus-filter`, and the arm is false.
  - At the fix `e04d2485`: `policy corpus -- 1 file(s) origin/main moved`, and the arm is true.

## Null control

- Arm 4 (old layout, an old `policy_lint` without `--corpus-filter`) prints `NOT compared` at both commits, so the sentinel probe is not weakened.
- The filer self-test run from `/Users/timmalmstrom/hpo-seats` (another working directory) passes and quotes the path relative to that directory.
- The dry run at the fix, `node tools/policy/friction_issues.mjs --dry-run --stats-file <57-PR histogram> --since v6.7.16`, exits rc=0 and would update #1985, #1990 and #2004 and file `other`. The same command at `main` exits rc=1 with `refusing: .claude/workflows/policy_lint.mjs --normalize-friction-keys did not answer`.

## Search rule

The moved-path search rule is stated in `dev/audit/rca/R9-RCA-2004.md` section 4 and was widened after the fix review. It now covers any line in a tracked `*.mjs *.js *.py *.sh *.yml` file, outside the frozen `tools/audit/round*/` and `dev/archive/` trees, that names one of the 140 `tests/layout.json` `retired.old` paths absent at HEAD and either assigns it to a constant, spawns or execs it, or **reads or imports it** (`readFileSync`, `open(`, `read_text`, `import(`, `require(`, `git show`, `git cat-file`). A hit is cleared by the new path on the same statement, a `locate()` resolution, or a `test -f` / `existsSync` shim that falls back to the new path. Re-run at `64c1744d`: four executed-and-broken seams (the three from the first rule plus the FR-3 consumer harness, now fixed), and no other executed hit. Left, named for R9-RO-8: usage docstrings that print a pre-move command and are not executed (`tools/coverage/partition.py`, `coverage_tree.sh`, `tests/coverage_ratchet.py`, `tools/policy/agreement_py.py`, `budget_raise_gate.py`, `tools/pr/contract_rerun.py`, `tools/devices/measure_prefill_corpus.py`, `custom_components/heatpump_optimizer/prefill_offer.py`; the last is under `custom_components/`, so a text-only change there would widen a closure).

## Figures

- `GITHUB_TOKEN=$(gh auth token) node tools/policy/policy_lint.mjs --stats --since v6.7.16`: `harness` 5 / 7, over 57 merged PRs, 50 of which carry a verdict.
- The seat's own enumeration, independent of `policy_lint.mjs`: `/commits/<sha>/pulls` over the first-parent commits, then each PR's comments matched against `^Fix review:\s+blocked\s+[0-9a-f]{40}\s+harness\s*:`. Result: 7 entries over #1960, #1983, #1986, #1993 (3), #1994. Reviews contribute 0.
- `gh run view <id> --json jobs`: `record: File the recurring-friction issues the histogram named` failed on runs 37531301054, 37551449435, 37559014577, 37564564652, 37568067978 and 37577849702. That is every push to `main` from `6001b09a` (#1919) to `3910026e`.
- `bash tools/pr/preflight.sh </dev/null`: `check policy corpus -- NOT compared` at `main`, and `ok policy corpus -- current with origin/main` at this head.
- `node tools/policy/rules_sync.mjs --check`: rc=0 at this head. With `.cursor/rules/defect-root-cause.mdc` reverted to the old path it returns rc=1, and after restoring it rc=0.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 40 policy file(s)`.
- `python3 tools/audit/fold_ledger.py check`: `97 rca entries`, `0 violation(s)`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 2 script(s) run, 29 scoped out` (`tests/entities.py`, `tests/harness_headers.py`).
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2189 ENTITY CHECKS PASSED` at `e59313f0`, and again at this head (673 s), including `ok   and compares in the moved layout, policy_lint.mjs under tools/policy/`. The first run of it hit `OSError: [Errno 28] No space left on device` (the disk had 4.0 GiB free) and the re-run passed.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `12 of 109 HARNESS HEADER CHECKS FAILED`. All 12 are `tools/audit/round4/D7/sysid_estimator_frontier.py`, which hit `wall limit 900s exceeded` with `cpu=197.6s` while `tests/entities.py` ran beside it. The diff touches neither that harness nor `custom_components/`. Left to CI.

## Red checks

`delivery-status` and `nightly-status` grade `main`. On `main`, record-autofix staged the old delivery path, and #2011 fixes that. This diff reaches neither check's inputs (their scripts, `tests.yml`, `governance.yml`, the plan, `dev/programme/HANDOVER.md`) except this pull request's own row, `dev/programme/delivery/2014.md`. A red on either is `main`'s and is not answered here. No other check has run red on a commit of this branch.

## Forward-carry

- R9-RO-8 (#1921): the 67 landed `tests/layout.json` `retired` entries still at `since: null`, program launches that spell a pre-move path and so skip `counts.mjs` `locate()`, and the usage docstrings listed under Search rule that print a pre-move command. The orchestrator carries all three into the R9-RO-8 roster brief.
- D13 (process yield): key the `harness` friction on its sub-reason once the sub-reason grammar is closed. Recommendation only.

## Friction

none

## Approval

`dev/governance/rules/defect-root-cause.md` "Where it is recorded" now names `dev/audit/rca/<id>.md` instead of `tools/audit/rca/<id>.md`, matching `tools/audit/fold_ledger.py`'s `RCA_DIR`. The generated copies were rewritten by `node tools/policy/rules_sync.mjs`: `.claude/rules/defect-root-cause.md` and `.cursor/rules/defect-root-cause.mdc`. This is a policy change. It corrects the location and does not change what a seat must do. The orchestrator approved it under mandate 5951564627.
