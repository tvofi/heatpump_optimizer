The root cause of the `harness` friction key (#2004), with the defect found while re-deriving its count fixed. Since #1919 moved `policy_lint.mjs` into `tools/policy/`, the friction filer spawned it at its old path (fixed on main by #2011; this branch also fixes the path it quotes), and the pre-flight has run it there. Every governance `record` run on `main` since then has refused at the friction step, and every pre-flight prints `policy corpus -- NOT compared`. Both now find the program where the tree keeps it. Each fix comes with a check that was committed first and shown failing.

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

`44f5103cf7825c93c06576b21a74b54d129ebad6`

## Mutation proof

- `tools/policy/friction_issues.mjs` (the spawn fix landed via #2011, `f060cb4c`; this branch kept only the quoted command):
  - #2011 made the filer spawn `policy_lint.mjs` where the tree keeps it and left `STATS_TOOL`, the path quoted as an issue's derivation command, at `.claude/workflows/policy_lint.mjs`. This branch now makes one constant serve both and adds a self-test arm.
  - With main's shape and the new arm only: `node tools/policy/friction_issues.mjs --self-test` rc=1, `FAIL and the stats tool quoted as an issue's derivation command is a file: .claude/workflows/policy_lint.mjs`, `101 passed, 1 failed`. At the merged tree: rc=0, `102 passed, 0 failed`.
  - Three-dot against `origin/main`, the PR's diff to this file is the 7-line addition above and nothing else; the earlier `STATS_TOOL_PATH` / `fileURLToPath` form was dropped in the merge.
- `tools/audit/harnesses/r9_fr3_family_consumer.mjs` (fix-review round 1 finding, line 43):
  - At `3d31fc52` (the line reads `.claude/workflows/friction_issues.mjs`): rc=1, `ENOENT: no such file or directory, open '.../.claude/workflows/friction_issues.mjs'`.
  - At the fix `64c1744d` (the line reads `tools/policy/friction_issues.mjs`): rc=0, all family arms `ok`, including `a producer that prints the family row without counting it refuses`. Restoring the old spelling gives the rc=1 again.
- `.github/workflows/governance.yml` (lines 220 and 602), shell logic over three bases, run in bash with the form as committed (`! cat-file new && ! cat-file old`): at `origin/main` the old form gives skip and the new form runs, for both `field_coverage.mjs` and `agreement.mjs`; at `6001b09a~1` (before #1919) both forms run. The first draft used a `{ ...; }` group, which `codeowners_gap.py --check` read as an unparseable line and answered `uncovered_files=8`; the committed form gives `uncovered_files=0`, as `origin/main` does. `node tools/policy/field_coverage.mjs` at this head: `FIELD COVERAGE ok`, `blind=0 dead=0 refused=0`.
- `tools/pr/preflight.sh`:
  - The detector commit `bf669af7` adds arm 5 to `tests/entities.py`'s stale-corpus fixture: the same stale head, with `policy_lint.mjs` under `tools/policy/` only.
  - The fixture, extracted and run on its own, gives at `bf669af7`: `policy corpus -- NOT compared: policy_lint.mjs here does not answer --corpus-filter`, and the arm is false.
  - At the fix `e04d2485`: `policy corpus -- 1 file(s) origin/main moved`, and the arm is true.

## Null control

- Arm 4 (old layout, an old `policy_lint` without `--corpus-filter`) prints `NOT compared` at both commits, so the sentinel probe is not weakened.
- The end-to-end dry run was measured before #2011 and is not re-claimed after the merge.

## Search rule

The moved-path search rule is stated in `dev/audit/rca/R9-RCA-2004.md` section 4. It covers any line in a tracked `*.mjs *.js *.py *.sh *.yml` file, outside the frozen `tools/audit/round*/` and `dev/archive/` trees, that names one of the 140 `tests/layout.json` `retired.old` paths absent at HEAD and either assigns it to a constant, spawns or execs it, or reads or imports it (`readFileSync`, `open(`, `read_text`, `import(`, `require(`, `git show`, `git cat-file`). A hit is cleared by the new path on the same statement, a `locate()` resolution, or a shim that falls back to the new path.

The earlier claim here that every other executed hit was cleared was wrong. The fix review wrote its own implementation of the rule (`widened_rule.py`) and found two more seams. Seven seams in all, counting the two `governance.yml` steps apart:

- Fixed on main or on this branch: `friction_issues.mjs` `STATS_TOOL`, `preflight.sh` `corpus_filter`, the env-matrix base driver, the FR-3 consumer harness, and `governance.yml` lines 220 (`field coverage`) and 602 (`agreement lane`), which checked the pinned base for the old path only, so every base after #1919 skipped both checks (main run 37626923348: `field coverage: the base does not carry it ... skipped`). They now try `tools/policy/` first and the old path second. Over a base that carries only `tools/policy/` the old test gives skip and the new one runs; over a pre-#1919 base both run.
- Owned by open PR #2012 (RCA-1990, `fix/r9-rca-1990`), not fixed here: `tools/audit/seat/merge_train.py:146,210` (`bash tools/audit/app_approve.sh`) and `:237` (`bash tools/audit/preflight.sh`), rc=127 from the repository root. #2012 re-points exactly these three calls through a `tool()` map.

Completeness evidence: the reviewer's `widened_rule.py`, run at head `44f5103cf7825c93c06576b21a74b54d129ebad6`, output verbatim:

```
retired.old absent at HEAD: 140
shape hits cleared by new-path/locate within +-4 lines: 99
UNCLEARED: 55
.claude/hooks/stop-selfcheck.sh:200: [tools/audit/prepr.sh] printf 'stop-selfcheck: this turn touched the policy corpus and policy_lint refuses it.\n%s\n\nRun `bash tools/audit/prepr.sh` before opening or updating a pull request.\
.claude/workflows/audit-fix.js:25: [tools/audit/README.md] `You own fix group ${group} of the audit: issues #${issues.join(', #')}. From ${repo}: git fetch origin; git worktree add ../audit-fix-${group} -b claude/audit-fix-${grou
.claude/workflows/audit-fix.js:25: [tools/audit/briefs/fixer.md] `You own fix group ${group} of the audit: issues #${issues.join(', #')}. From ${repo}: git fetch origin; git worktree add ../audit-fix-${group} -b claude/audit-fix-${grou
.claude/workflows/audit-verify.js:248: [.claude/workflows/brief_lint.mjs] One issue per class, not per finding (PLAN section 8.1). Classes: ${JSON.stringify(classes)}. Write tools/audit/round${round}/ISSUES.json: per class {class, title: "[R${r
.claude/workflows/audit-wave.js:48: [tools/audit/README.md] `You own fix group ${group} of the audit: issues #${issues.join(', #')}. From ${repo}: git fetch origin; git worktree add ../audit-fix-${group} -b claude/audit-fix-${grou
.claude/workflows/audit-wave.js:48: [tools/audit/briefs/fixer.md] `You own fix group ${group} of the audit: issues #${issues.join(', #')}. From ${repo}: git fetch origin; git worktree add ../audit-fix-${group} -b claude/audit-fix-${grou
.claude/workflows/web-fix-wave.js:304: [tools/audit/briefs/fix-review.md] Read tools/audit/briefs/fix-review.md and follow it. You are not checking that the code looks right; four implementations on this project looked right and were wrong, one
.claude/workflows/web-fix-wave.js:342: [tools/audit/app_approve.sh] - resume.stage is 'merge' but there is no "Fix review: merge" comment at the CURRENT head (a verdict at an older head counts only when bash tools/audit/app_approve.sh --c
.github/workflows/pr-contract.yml:279: [.claude/workflows/policy_lint.mjs] node .claude/workflows/policy_lint.mjs \
custom_components/heatpump_optimizer/prefill_offer.py:21: [tools/measure_prefill_corpus.py] PYTHONPATH=tests/hastub python3 tools/measure_prefill_corpus.py
tests/entities.py:17465: [tools/audit/preflight.sh] ["bash", "tools/audit/preflight.sh"], cwd=str(d), input="a body\n",
tests/entities.py:17619: [tools/audit/preflight.sh] ["bash", "tools/audit/preflight.sh"], cwd=str(d), input="a body\n",
tools/audit/seat/merge_train.py:146: [tools/audit/app_approve.sh] code, o = self.run(["bash", "tools/audit/app_approve.sh", self.repo, str(pr), h])
tools/audit/seat/merge_train.py:210: [tools/audit/app_approve.sh] o = self.run(["bash", "tools/audit/app_approve.sh", "--carry", v, h])[1]
tools/audit/seat/merge_train.py:237: [tools/audit/preflight.sh] pf = self.run(["bash", "tools/audit/preflight.sh", *map(str, item.get("issues", []))], stdin=title + "\n")[1]
tools/coverage/partition.py:43: [tools/audit/w5-partition/] python3 tools/audit/w5-partition/partition.py --coverage $W/out/coverage.json
tools/devices/measure_prefill_corpus.py:8: [tools/measure_prefill_corpus.py] PYTHONPATH=tests/hastub python3 tools/measure_prefill_corpus.py
tools/policy/agreement.mjs:29: [.claude/workflows/agreement.mjs] //   node .claude/workflows/agreement.mjs [--only pairs|discovery]
tools/policy/agreement.mjs:69: [.claude/workflows/agreement_py.py] if (i < 0 || !process.argv[i + 1]) throw new Error('no --py-json FILE: run `python3 -I .claude/workflows/agreement_py.py --run`')
tools/policy/agreement_py.py:3: [.claude/workflows/agreement_py.py] python3 -I .claude/workflows/agreement_py.py --out FILE   # writes the JSON
tools/policy/agreement_py.py:4: [.claude/workflows/agreement_py.py] python3 -I .claude/workflows/agreement_py.py --run        # writes it, then runs agreement.mjs on it
tools/policy/brief_lint.mjs:40: [.claude/workflows/brief_lint.mjs] //   node .claude/workflows/brief_lint.mjs [files...]
tools/policy/budget_raise_gate.py:57: [.claude/workflows/budget_raise_gate.py] python3 -I .claude/workflows/budget_raise_gate.py --base SHA --head SHA --pr N [--repo O/R]
tools/policy/budget_raise_gate.py:58: [.claude/workflows/budget_raise_gate.py] python3 .claude/workflows/budget_raise_gate.py --self-test
tools/policy/budget_raise_gate.py:59: [.claude/workflows/budget_raise_gate.py] python3 -I .claude/workflows/budget_raise_gate.py --rerun-stale RUN_ID [--repo O/R]
tools/policy/check-wave-script.mjs:11: [.claude/workflows/check-wave-script.mjs] //     node .claude/workflows/check-wave-script.mjs
tools/policy/field_coverage.mjs:39: [.claude/workflows/field_coverage.mjs] //   node .claude/workflows/field_coverage.mjs [--only hooks|ruleset|budgets|approvals|registry|census]
tools/policy/field_coverage.mjs:41: [.claude/workflows/field_coverage.mjs] //   node .claude/workflows/field_coverage.mjs --self-test
tools/policy/field_coverage.mjs:119: [.claude/workflows/policy_lint.mjs] const { code, out } = await run('node', [at('.claude/workflows/policy_lint.mjs'), '--hooks', path.relative(ROOT, f)])
tools/policy/field_coverage.mjs:206: [.claude/workflows/fixtures/] function ruleFixture() { return JSON.parse(fs.readFileSync(at('.claude/workflows/fixtures/required-contexts.json'), 'utf8')) }
tools/policy/figure_census.mjs:170: [.claude/workflows/policy_lint.mjs] ok(templated('node .claude/workflows/policy_lint.mjs --budgets') === null,
tools/policy/figure_lint.mjs:600: [tools/audit/prepr.sh] const inside = analyse('bash tools/audit/prepr.sh')
tools/policy/friction_issues.mjs:51: [.claude/workflows/friction_issues.mjs] //   node .claude/workflows/friction_issues.mjs --stats-file <path> --since <ref>
tools/policy/friction_issues.mjs:52: [.claude/workflows/friction_issues.mjs] //   node .claude/workflows/friction_issues.mjs --stats-file <path> --since <ref> --dry-run
tools/policy/friction_issues.mjs:53: [.claude/workflows/friction_issues.mjs] //   node .claude/workflows/friction_issues.mjs --self-test
tools/policy/policy_lint.mjs:41: [.claude/workflows/policy_lint.mjs] //   node .claude/workflows/policy_lint.mjs            # lint + acceptance (CI)
tools/policy/policy_lint.mjs:42: [.claude/workflows/policy_lint.mjs] //   node .claude/workflows/policy_lint.mjs --list     # every check + fixture
tools/policy/policy_lint.mjs:43: [.claude/workflows/policy_lint.mjs] //   node .claude/workflows/policy_lint.mjs --budgets  # sizes vs caps
tools/policy/policy_lint.mjs:44: [.claude/workflows/policy_lint.mjs] //   node .claude/workflows/policy_lint.mjs --hooks [settings.json]  # wired and self-testing
tools/policy/policy_lint.mjs:45: [.claude/workflows/policy_lint.mjs] //   node .claude/workflows/policy_lint.mjs --report   # enforcement summary
tools/policy/policy_lint.mjs:46: [.claude/workflows/policy_lint.mjs] //   ... | node .claude/workflows/policy_lint.mjs --corpus-filter  # keep the policy paths
tools/policy/policy_lint.mjs:47: [.claude/workflows/policy_lint.mjs] //   node .claude/workflows/policy_lint.mjs <files...> # lint just these
tools/policy/policy_lint.mjs:48: [.claude/workflows/policy_lint.mjs] //   node .claude/workflows/policy_lint.mjs --record-known-bad   # reseed the ratchet
tools/policy/policy_lint.mjs:49: [.claude/workflows/policy_lint.mjs] //   node .claude/workflows/policy_lint.mjs --pr-body <file> --head <sha> [--title t] [--red names] [--paths-file f] [--existing-file f] [--author login]
tools/policy/policy_lint.mjs:50: [.claude/workflows/policy_lint.mjs] //   node .claude/workflows/policy_lint.mjs --record --since <ref>   # dispositions
tools/policy/policy_lint.mjs:51: [.claude/workflows/policy_lint.mjs] //   node .claude/workflows/policy_lint.mjs --stats  --since <ref>   # histograms
tools/policy/policy_lint.mjs:52: [.claude/workflows/policy_lint.mjs] //   node .claude/workflows/policy_lint.mjs --sunset --since <ref>   # dead rules
tools/policy/policy_lint.mjs:1032: [.claude/workflows/fixtures/] const FIXTURE_CAP_PREFIX = '.claude/workflows/fixtures/'
tools/policy/policy_lint.mjs:1052: [.claude/workflows/fixtures/] const REQUIRED_CONTEXT_FIXTURE = '.claude/workflows/fixtures/required-contexts.json'
tools/policy/record-predicate/row_files_replay.py:19: [tools/audit/record-predicate/] python3 tools/audit/record-predicate/row_files_replay.py [branch-ref ...]
tools/policy/rules_sync.mjs:10: [.claude/workflows/rules_sync.mjs] //   node .claude/workflows/rules_sync.mjs           # regenerate
tools/policy/rules_sync.mjs:11: [.claude/workflows/rules_sync.mjs] //   node .claude/workflows/rules_sync.mjs --check   # refuse if out of date
tools/pr/contract_rerun.py:20: [.claude/workflows/contract_rerun.py] python3 -I .claude/workflows/contract_rerun.py --rerun RUN_ID [--repo O/R]
tools/pr/contract_rerun.py:21: [.claude/workflows/contract_rerun.py] python3 .claude/workflows/contract_rerun.py --self-test
tools/pr/prepr.sh:556: [.claude/workflows/budget_raise_gate.py] exec(compile(open(src).read(), f"{base[:12]}:.claude/workflows/budget_raise_gate.py", "exec"), m.__dict__)
```

Triage of the 55 uncleared, by reading and not by a second script: the three `merge_train.py` lines (owned by #2012 above); usage docstrings and comments that print a pre-move command and run nothing (carried to R9-RO-9); `analyse(...)` and `templated(...)` string inputs to self-tests; `locate()`-resolved fixture constants in `policy_lint.mjs` and `field_coverage.mjs`; `pr-contract.yml:279`, which sits under a `test -f` shim beyond the four-line window; the label string at `prepr.sh:556`; and `tests/entities.py:17465,17619`, which run in a fixture directory.

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

- R9-RO-8 (#2015, still open): the 67 landed `tests/layout.json` `retired` entries still at `since: null`, and program launches that spell a pre-move path and so skip `counts.mjs` `locate()`. R9-RO-9: the usage docstrings that print a pre-move command, whose roster entry carries them with the widened rule as the control.
- D13 (process yield): key the `harness` friction on its sub-reason once the sub-reason grammar is closed. Recommendation only.

## Friction

none

## Approval

`dev/governance/rules/defect-root-cause.md` "Where it is recorded" now names `dev/audit/rca/<id>.md` instead of `tools/audit/rca/<id>.md`, matching `tools/audit/fold_ledger.py`'s `RCA_DIR`. The generated copies were rewritten by `node tools/policy/rules_sync.mjs`: `.claude/rules/defect-root-cause.md` and `.cursor/rules/defect-root-cause.mdc`. This is a policy change. It corrects the location and does not change what a seat must do. The orchestrator approved it under mandate 5951564627.

`.github/workflows/governance.yml` is code-owned, and this diff changes two lines of it (the pinned-ref probes at lines 220 and 602, see Search rule), so it needs tvofi's approving review.
