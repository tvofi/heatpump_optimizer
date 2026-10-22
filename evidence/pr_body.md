R10-CI-LAYOUT PR 1: the nightly lanes leave tests.yml, the pin plan folds into mutation, recheck-gate goes, and W1 removes the C1 composition at its source

Part of #2495 and of #201. Group: R10-CI-LAYOUT-P1 (roster `handoff/audit-r10-roster`), PR 1 of the four-PR CI-layout sequence. PR 0 merged as #2464 and PR G as #2529 (`5a755f53e`). The design is phase 1 of `probe/design-ci-rev4` (`1371a0a6`, archived as the tag `archive/probe/design-ci-rev4`), approved at review round 5 (`archive/probe/design-ci-review5`, `afc00bfe`). This PR builds DESIGN-P1 less step 5b, which PR 0 landed. It includes W1 and B9's producer check.

**Owner gate.** This PR is code-owned CI workflows (`/.github/workflows/`, and `/.github/actions/`, which this PR adds to CODEOWNERS) and policy (`dev/governance/rules/ci-autofix.md`, `defect-root-cause.md`, their `rules_sync` outputs, and decision 0011's workflow paragraph). It also raises one row of `tests/ci_budgets.json` (see `## Raise justification`). The CODEOWNER session approves it at its merged head under mandate 6329234399, which replaces 6319294694 (`## Red checks`, `budget-raise-gate`). No required context is added, renamed or removed.

**Round 3 (this head).** The branch was approved at `e93de8667`. Merging current main made `tools/pr/prepr.sh` step 6d refuse it: `PREDICT closures INERT READS tests/entities.py: tools/audit/seat/orchestrator_tick.py (a new file beside 6 it lists)`. This round merges main and shows that prediction is false. It then fixes the predictor rather than writing the entry `--apply-inert` offered.

- **The read is not one CI records.** `closure.strace_files` counts only Python processes and their non-exec forks. Under `strace -f`, no Python process of `tests/entities.py`'s run opens `orchestrator_tick.py`, as source or as `.pyc` (`## Figures`). Its readers are the `policy_lint.mjs` node child, which opens all of `tools/audit/seat/`, and git's content scans. The recorder counts neither.
- **CI measured it already.** At `e93de8667` the file was already changed. `closure-scope` (job 119513712926) printed `Every closure is re-derived, exactly as on a push to main.`, and both `closures` runs at that head concluded `success` (119513881017, 119513806248).
- **Why it fired.** `ci_predict.inert_siblings` reads three listed siblings of one directory and suffix as a glob. `tests/entities.py`'s committed `inert_reads` lists six `tools/audit/seat/*.py` files. Five of them have since left INERT and stay listed: `merge_train.py`, `queue_pre_flight.py`, `record_row.py`, `roster_lib.py` and `tmp_paths.py`. A glob files only INERT siblings under `inert_reads`, so those five are not evidence of a glob. Commit `188c5728b` counts a sibling only while it is INERT. `prepr.sh --self-test` gains a pair of arms: a planted reader listing three siblings that left INERT stays quiet, and the same reader listing three INERT siblings still predicts (M8).

**Round 2** made `instrument-self-tests` green. It was red at `31cf0426` on `ref_privacy.py --check` (`REFUSE .github/workflows/nightly.yml:381: a push site in a file PUSHERS does not name`). Commit `e4294cde5` registers `nightly.yml` as `republishes`, and `tests.yml`'s entry keeps only the pull-request-branch reason.

What changes (DESIGN-P1 section 2, read from the ref):

- **(a) `nightly.yml` (`name: Nightly`).** It carries `mutation-nightly`, `mutation-ledger`, `mutation-ledger-push`, `slow`, the schedule and dispatch arm of `nightly-ha`, and `record-autofix`.
  - Its triggers are `schedule: 17 2 * * *` (the one cron, moved), `workflow_dispatch`, and `push: main` (for `record-autofix` alone).
  - Floor `contents: read`; concurrency by run id, never cancelled.
  - Each moved job is verbatim except its `if:` (the recheck clause and `needs: [recheck-gate]` go). That includes `record-autofix`'s automerge step, so its train-hold arm is kept (Lean study K6, carried to this group).
  - `tests.yml` drops `schedule:` and the schedule arm of `coverage`.
  - `nightly-ha` keeps only its pull-request arm in `tests.yml`. Both arms run the composite action `.github/actions/nightly-ha`, so each keeps its `nightly-ha (<image>)` check name.
  - `tests/nightly_status.py` reads `nightly.yml`, and so does its red report's dispatch call. `REQUIRED_LANES` is unchanged.
  - D-1: the record beat's red no longer reddens the Tests push run. The tick still flags it: see the D-1 test below.
  - `tools/audit/seat/ref_privacy.py` `PUSHERS` names `nightly.yml` for the pushes that moved (round 2).
- **(b)** `mutation-pin-plan` is folded into `mutation` as its last step: `id: plan`, `if: always()`, with `outputs: shards, count`. `mutation-pins` needs `[mutation]`.
- **(c) W1 (owner ruling D-4): the C1 composition is removed at its source.**
  - `coverage_tree.sh`'s composed branch and its `closure.py composed-list` call.
  - `derive_closures.sh`'s `COMPOSED_CONSUMED` case.
  - `closure.py`'s `COMPOSED`, `CHEAP_ARGV_OR_ENV`, `composed_verify`, `composed_compare`, their subcommands and self-tests, and the `INERT_EXCEPT` entry for the proof driver.
  - `coverage`'s strace install and its `composed-closures` upload.
  - `closures`' `needs: coverage` and its two consume steps.
  - The `composed-proof` job, `tests/composed_closures.json` and `tools/coverage/composed_proof.sh`.
  - `python3 tests/closure.py prune` dropped the three phantom entries in `tests/closures.json`.
- **(d)** `recheck-gate` is deleted. Each `needs.recheck-gate.outputs.recheck == 'true'` arm becomes `github.event_name == 'workflow_dispatch'`. The `recheck` and `no-skip` inputs stay declared, because `merge_train.py` dispatches with `-f recheck=true`.
- **B9.** `tests/entities.py` now checks that every required context `tests.yml` produces runs on an autofix dispatch (no inputs) and on a batch-proof dispatch (`recheck=true`), and needs no job that `tests.yml` lacks. A null control plants the old recheck-gate arm.
- **Readers:**
  - `entities.py`: `_NIGHTLY_YML`, the composite-action reader, and the schedule-only derivation, now evaluated over `nightly.yml`'s `if:`s with a null control.
  - `entities.py`: the record beat, ledger, reach, cron and slow readers, the folded-plan wiring pin and its three null plants, the no-C1-token pin, and the action-pin check extended to `.github/actions`.
  - `closure.py` `GATE_FILES` gains `nightly.yml` and the action.
  - `merge_main_bot.py` `PIN_CHAIN` (three jobs), `merge_train.py` (its beat self-test reads `nightly.yml`), `policy_lint.mjs` `REPORTER_INPUTS` (gains `nightly.yml`), `ref_privacy.py` `PUSHERS` (round 2), and the `ci-watch.sh` fixtures.
  - `CODEOWNERS` gains `/.github/actions/`; `tests/README.md` is updated.
  - `r10_replay_loopnorm.py` reads `slow` from both workflow files.
- **Carried in:** the four stale "a GITHUB_TOKEN push leaves no pull_request run" comments in `tests.yml` (#2394's Friction) now state the measured fact: a bot head's runs are created, held `action_required`, and approved by hpo-runs.
- **Round 3:** `tools/pr/ci_predict.py`'s `inert_siblings` counts only INERT siblings, and `tools/pr/prepr.sh --self-test` pins it (above).

**Deviation from the design, with its evidence.** DESIGN-P1 2(a) deletes `coverage`'s step "Check the restored coverage is main's push run's". Its premise is that the step "executed on the schedule run only" (section 0, item 5). At this base the premise is false.

- The step gates per-script coverage reuse (`W5P_REUSE`) on every pull request with a cache hit, and `entities.py`'s `_cov_steps` pins it.
- Round 1 read the saved `tests_jobs_<run>.json`'s `coverage` steps by name, over the 90 PR runs in the critical-path fetch whose four lanes concluded. The step executed 53 times and was skipped 31 times. That count is of CI runs dated 2026-10-21, not of this tree, and is not re-taken (`## Figures`).

So it is kept. Deleting it would let an unverified cache entry stand in for the base's measurement. The step is not on the static map's drop list, and the static check below passes with it kept.

## Head

`e817bb123b46b6ecee2e2516966dcb48d6061e27` merges the authored code head `188c5728b00a8cb746b1ff31b35c0030b3842eb1` and then merges origin/main `3976515a0` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`188c5728b00a8cb746b1ff31b35c0030b3842eb1`. It is the approved PR head `e93de8667` plus two commits:

- `adc94f5eb`: a merge of origin/main `93e6a63d2855651448a2b8f677b392feddc03c99` into `e93de8667`. Its one conflict was `dev/programme/HANDOVER.md`. The branch's only edit there corrected `tests.yml` to `nightly.yml` in a sentence that main's rewrite deleted, so main's text is taken whole. `tests/closures.json` merged through the ledger driver.
- `188c5728b`: the round-3 predictor fix (`tools/pr/ci_predict.py`, `tools/pr/prepr.sh`).

`git merge-base HEAD origin/main` is `93e6a63d2855651448a2b8f677b392feddc03c99`. That is origin/main's tip, read at 2026-10-22T01:41:43Z, so the branch is 0 commits behind. `git diff --stat $(git merge-base origin/main HEAD)...HEAD` reads `39 files changed, 1941 insertions(+), 2125 deletions(-)`.

Every figure below was re-taken at this head unless it says otherwise. The entities, mutant and trace runs ran on `702741a5f`. That commit is this head's tree (`9c3982817`) under an earlier message, so its runs measure this tree. Every local figure was taken on a Linux cloud seat under `/opt/hpo/venv-ci` (CPython 3.14.7). The critical-path figures and the coverage-step count are round 1's CI-run figures. Their dates are under `## Figures`.

## Mutation proof

Round 3's fix:

- **M8.** In a throwaway detached worktree at this head, restore `inert_siblings`' old predicate (count every listed sibling). `git diff --stat` reads `1 file changed, 1 insertion(+), 2 deletions(-)`.
  - `bash tools/pr/prepr.sh --self-test` reads `310 passed, 1 failed`, rc 2. The one failure is `6d reads no glob from three listed siblings that left INERT, which a glob never files there (R10-CI-LAYOUT-P1) (got 0, wanted 1)`.
  - `python3 tools/pr/ci_predict.py --base origin/main` prints the round's red again: `PREDICT closures INERT READS tests/entities.py: tools/audit/seat/orchestrator_tick.py (a new file beside 6 it lists)`, rc 1.
  - At this head the self-test reads `311 passed, 0 failed` and the predictor rc 0 (`## Figures`).

Rounds 1 and 2's elements, re-run together at this head's tree in one throwaway detached worktree (uncommitted, `git diff --stat`: `4 files changed, 5 insertions(+), 10 deletions(-)`). Each mutant touches a different artifact, so each failing check names its own mutant. `PYTHONPATH=tests/hastub python tests/entities.py` read `6 of 2388 ENTITY CHECKS FAILED`, rc 1. Diffed against the unmutated head's run, the new failures are exactly these:

- M1 (B9): `briefs`' dispatch arm restored to `(workflow_dispatch && needs.recheck-gate.outputs.recheck == 'true')` → `every required context tests.yml produces runs on an autofix or batch-proof dispatch (B9)`.
- M2 (b): `if: always()` deleted from `mutation`'s plan step → `the pin shard count scales with the diff's new sites ... (plan wiring=False)`.
- M3 (W1): `closures` given `needs: [closure-scope, coverage]` again → `the C1 composition stays removed at its source (W1): no carrier names a C1 token`.
- M4 (a): `nightly_status.DEFAULT_WORKFLOW` back to `tests.yml` → `the reporter watches exactly the lanes a pull request cannot see`.
- M5 (a): `nightly.yml`'s `nightly-ha` no longer calls the action → `both nightly-ha arms check out, then run the shared composite action on their matrix image`.
- M6 (a): `mutation-ledger`'s main ref guard deleted → `a branch-ref dispatch reaches neither mutation-ledger nor mutation-ledger-push; ...`.
- M7 (round 2): `nightly.yml`'s two-line `PUSHERS` entry deleted. `entities.py` kills none of the seven mutants beyond these six. `python3 -I tools/audit/seat/ref_privacy.py --check` in the same worktree reads `REFUSE .github/workflows/nightly.yml:381: a push site in a file PUSHERS does not name` and `1 refused`, rc 1. That is governance's `instrument-self-tests` step, M7's killer.

The diff also shows one changed line that is not a new failure. `a8:register_once` is a planted-negative fixture line, and it prints in both runs with a different sample of `__dup` names.

`ref_privacy.py`'s reason text is unpinned, by the registry's design. `registry_refusals` keys on the path, and on `guarded` versus a reason, never on the reason's words. M7 is the mutant that removes the predicate's input.

Self-test mutants, each in a second throwaway worktree and restored:

- `PIN_CHAIN` given `mutation-pin-plan` back: `merge_main_bot self-test: 40 checks, 1 failed`. The failing check is "while mutation runs ... the retired mutation-pin-plan name is no chain job".
- `nightly.yml`'s `record-autofix` renamed: `orchestrator_tick self-test: 176 checks, 1 failed` (`MAIN D-1: nightly.yml's push-run jobs are exactly the record beat`). Round 1 read 2 failed at `172` checks. Main's newer checks changed the self-test's shape, and the D-1 arm still kills this mutant.

The static null control's own plant is under `## Null control`.

## Null control

- **Round 3's.** The fixed predicate sees the same plant twice. A reader listing three siblings that left INERT gives no prediction. The same reader listing three INERT siblings is still predicted (`and predicts it from three listed INERT siblings, the same plant otherwise (null control)`: `ok`). The fix narrows which listed entries are evidence of a glob, and the true-glob case still fires. The self-test's existing `pinert` arm (a new harness beside `tests/harness_headers.py`'s listed INERT harnesses) also still passes.
- **The trace's positive control.** The same process rule over the same trace finds Python processes opening `tools/audit/seat/record_row.py` (7 processes, its self-test child and the main process) and `merge_train.py` (the main process). It finds `roster_lib.cpython-314.pyc` loaded by 41. So the zero for `orchestrator_tick.py` (source and `.pyc`) is not an instrument that sees nothing.
- **Round 2's.** The unmodified round-1 head `31cf0426` printed `1 refused`, rc 1, for `ref_privacy.py --check`, and this head prints `0 refused`, rc 0. Its self-test `ref_privacy self-test: 66 checks, 0 failed` is unchanged.
- The unmutated head: `ALL 2388 ENTITY CHECKS PASSED`, rc 0 (`PYTHONPATH=tests/hastub python tests/entities.py`).
- The **static** half of the design's null control (DESIGN-P1 section 4, `measure/rev/unitcheck2.py static`) uses a closed map, committed as `dev/audit/harnesses/r10_ci_layout_p1/unitcheck_map.json`.
  - Head: `STATIC rows 225->232 lost 0 gained 0 changed 29 (mapped 29) misplaced 0 rc 0`.
  - Planted: deleting one step from `nightly.yml`'s `record-autofix` (a verbatim move must keep it) gives `STATIC rows 225->231 lost 1 gained 0 changed 29 (mapped 29) misplaced 0 rc 1  (1 LOST row(s))`.
  - Each admitted `changed` row is printed before and after by the same run.
  - `record-autofix` and `mutation-ledger-push` show no row at all: they moved verbatim.
- The **runtime** half (DESIGN-P1 section 4's table) needs this PR's own CI runs and post-merge runs, so it is the orchestrator's. Its pairs are unchanged from the design. The `nightly` and `pin chain` rows are checked after the merge (risks R-2, R-4).
- The critical-path harness's self-test reads `edge+tail gain 330 s (want 330) ok; null control 0 s (want 0) ok`. The null control is a run whose `closures` already ends before `coverage`.

## Figures

- **The round's red, before the fix.** `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`, at `adc94f5eb` (the merge, before `188c5728b`): `PREDICT closures INERT READS tests/entities.py: tools/audit/seat/orchestrator_tick.py (a new file beside 6 it lists)` and `CI PREDICT: 1 predicted red(s) on closures against 93e6a63d2855`. At this head: `CI PREDICT: no closures or fast red predicted against 93e6a63d2855 (a data-file read is not seen)`, rc 0.
- **The listed siblings.** Read from `tests/closures.json` at this head: `inert_reads["tests/entities.py"]` lists six `tools/audit/seat/*.py` files. Of those, `closure.is_inert` is true for `selftest_wiring.py` alone. `git ls-files tools/audit/seat/` has 55 files, 45 of them INERT. 44 of the 45 are listed in neither of `tests/entities.py`'s tables, `orchestrator_tick.py` among them.
- **The trace.** Run at this tree: `PYTHONPATH=tests/hastub strace -f -qq -e trace=openat,open,execve,stat,newfstatat -o ent.strace python3 tests/entities.py`, rc 0, `ALL 2388 ENTITY CHECKS PASSED`.
  - A scratch probe applied `closure.strace_files`' process rule to that log, using its own `_STRACE_PID`, `_STRACE_EXEC`, `_STRACE_RESUMED`, `_STRACE_SPAWN` and `_STRACE_RET`. That rule counts a process whose last exec was a Python interpreter, and what it forks without exec. The probe read `python pids 200 python pids opening tools/audit/seat/orchestrator_tick.py : 0`, and the same for `orchestrator_tick.cpython-314.pyc`.
  - Every non-ENOENT `openat` of the file is in a non-Python process. Two are `node tools/policy/policy_lint.mjs` (pids 15759 and 16760). Each opens all 51 `tools/audit/seat/` files its corpus walk reaches. The rest are git processes reading the tree.
  - The probe is a one-off and stays in scratch. Its rule is `closure.strace_files`', and CI's FULL `closures` run at `e93de8667` is the committed instrument's own reading.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: `ref_privacy --check at HEAD: 20 file(s) with a push site, 9 guarded, 1019 line(s) added since 93e6a63d2855 judged, 0 refused`, rc 0. M7 makes it print `1 refused`.
- `python3 -I tools/audit/seat/ref_privacy.py --self-test`: `ref_privacy self-test: 66 checks, 0 failed`.
- `python3 -I tools/audit/seat/ref_privacy.py --check` took 0.70 s, measured with `date +%s.%N` either side of the run, at `adc94f5eb`. This is the cost under `## Red checks`.
- **The class, round 2.** The rule that enumerates the seams is `ref_privacy.sites(ref_privacy.grep("HEAD"))` checked by `registry_refusals`, which is what `--check` runs. Every push site under `tools/`, `.claude/workflows/` and `.github/workflows/` (20 files) gets a registry verdict, so no moved push site is unjudged. The two files whose push sites this PR changes:
  - `tests.yml`, sites at lines 2344, 2616 and 2904 (`closures-autofix`, `claims-autofix`, `mutation-autofix`): already registered, reason narrowed in this diff;
  - `nightly.yml`, sites at lines 381, 746 and 867 (`mutation-ledger-push`, `record-autofix` twice): registered in this diff.
- **The wider class: a path-keyed registry that names `tests.yml` and now owes `nightly.yml`.** The command is `git grep -l -E "workflows/tests\.yml" -- tools tests .claude/workflows .github ':!dev'`, with each file's `nightly.yml` count beside it. It returns 19 files.
  - 7 name `nightly.yml`: `tests.yml`, `tests/README.md`, `closure.py`, `entities.py`, `merge_train.py`, `ref_privacy.py` and `policy_lint.mjs`.
  - `tests/closures.json` names it since the bot's re-record.
  - The other 11 read `tests.yml` for what stays there, so each is already right:
    - fixtures: `card.mjs`, `lane_skip.py`, `budget_raise_gate.py`, `contract_rerun.py`, `stamp.py`;
    - comments: `run.sh`, `stress.py`;
    - the pull-request dispatch arms: `a1_dispatch_arms.sh`;
    - `pull_request` autofix runs: `autofix_statuses.sh`;
    - the job count `counts.mjs` publishes as `tests.yml`'s own;
    - `PIN_CHAIN`'s three `tests.yml` jobs: `merge_main_bot.py`.
- Governance's `instrument-self-tests` steps, each run from `governance.yml`'s own `run:` text with `RUNNER_TEMP` set to a temp directory:
  - `sweep_render self-test: 21 checks, 0 failed`; `policy_reread_check self-test: 15 checks, 0 failed`;
  - `orchestrator_tick self-test: 176 checks, 0 failed` (`172` at origin/main `93e6a63d2`; the four new checks are `MAIN D-1`);
  - `selftest_wiring: 73 self-testing, 73 wired, 0 unwired`, rc 0, the same line as at origin/main;
  - `throwaway_git: 0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`;
  - `merge_train self-test: 198 checks, 0 failed`; `queue_pre_flight self-test: 41 checks, 0 failed`;
  - `train.sh self-test: ok (5 refusals shown, root and options reach the child, no unasked flag)`.
- `git diff --stat $(git merge-base origin/main HEAD)...HEAD | tail -1`: `39 files changed, 1941 insertions(+), 2125 deletions(-)`.
- M8, `bash tools/pr/prepr.sh --self-test` in the mutant worktree: `310 passed, 1 failed`, rc 2 (`## Mutation proof`).
- `bash tools/pr/prepr.sh --self-test`: `311 passed, 0 failed`. At origin/main `93e6a63d2` it reads `309 passed, 0 failed`; the two new arms are round 3's.
- `PYTHONPATH=tests/hastub python tests/entities.py`: `ALL 2388 ENTITY CHECKS PASSED`, rc 0. The `FAIL` lines in its output are its self-test fixtures' planted negatives. The mutant run prints the same lines, and the diff of the two runs is under `## Mutation proof`.
- **Critical path (round 1's CI-run figures, not re-taken).** Their input is CI's own runs, not this tree. It is the 37 newest `pull_request` runs of `tests.yml` whose four lanes concluded, read 2026-10-21 by `dev/audit/harnesses/r10_ci_layout_p1/critpath_fetch.sh`. That fetch reads job logs from a host this seat's proxy refuses (`## Friction`).
  - `python3 -I dev/audit/harnesses/r10_ci_layout_p1/critpath.py RAW CASES --case SCOPED --n 20`: `SCOPED: runs 20; wall median 34.9 min; W1 gain median 8.8 min, min 0.0, max 14.4; runs gaining > 0: 19`.
  - The method is the design's phase-2 critical-path counterfactual (the `critpath` measure on the archived design tag). Every job's duration is held fixed; `closures` starts its measured queue after `closure-scope` instead of after `coverage`; `composed-proof` adds no tail.
  - The same with `--case FULL`: `FULL: runs 13; wall median 63.8 min; W1 gain median 18.1 min, min 0.0, max 35.6; runs gaining > 0: 11`. All 13 FULL cases name a gate file: `tests/closures.json` 7, `tests/closure.py` 4, `tests/requirements-ci.txt` 1, `.github/workflows/tests.yml` 1.
  - **The flow study's claim, corrected.** The model says W1 removes "about 7 min on a FULL-scope train and 19-21 min on a scoped run". On these runs the ordering is the reverse: a scoped run's median gain is 8.8 min and a FULL run's is 18.1 min. On a FULL run `closures` re-records everything and waited for `coverage`'s whole traced suite. On a scoped run it re-records little, and `fast` more often ends the run. Both figures are the design's model over measured job times, not a measured post-W1 run. The post-merge runs are the check.
- `sh dev/audit/harnesses/r10_ci_layout_p1/unitcheck.sh`: `head:    STATIC rows 225->232 lost 0 gained 0 changed 29 (mapped 29) misplaced 0 rc 0`, `plant:   STATIC rows 225->231 lost 1 gained 0 changed 29 (mapped 29) misplaced 0 rc 1  (1 LOST row(s))` (`## Null control`).
- `sh dev/audit/harnesses/r10_ci_layout_p1/c1_consumers.sh HEAD` (the design's own C1 census, read from `archive/probe/design-ci-rev4`): its `--- files:` list names 8 files. None is under `.github/` or `tools/coverage/`, and the one under `tests/` is `tests/entities.py`, whose hits are the no-C1-token pin's own pattern. Each file's disposition:
  - `merge_train.py` and `orchestrator_tick.py`: the design's kept fixtures (`composed-proof` as a never-concluding lane);
  - `tools/audit/carry_audit.py` and `dev/audit/harnesses/r10_verdict_item_barrier.py`, both from main since round 2: verdict-text fixtures that quote "composed-proof is not a required check". Neither reads the composition;
  - `dev/audit/harnesses/r10_carry_sweep_rows.py`: a round record naming the old job;
  - `dev/audit/harnesses/r10_ci_layout_p1/critpath.py` and `unitcheck_map.json`: this PR's measurement, which must name the deleted job to model it;
  - `tests/entities.py`: the pin.
  - At origin/main (`93e6a63d2`) the same command lists 14 files.
- `PYTHONPATH=tests/hastub python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: FULL -- every test script runs, nothing is scoped out.`, reason `.github/actions/nightly-ha/action.yml changes the gate itself, so every closure is suspect`. That is a gate file, as the design says. The CI `closures` FULL arm and `closures-autofix` own the re-recording, and no seat ran `derive_closures.sh` here (`PREPR_SKIP_CLOSURES=1`).
- The every-script-once count is 54: `closure.test_scripts()` less `SLOW_GATED` is 34, and coverage_tree.sh's `fast` stage, run by bash, is 20. This is `_cir_once_count()`'s rule in `tests/entities.py`, pinned equal to the budget row, run by a scratch copy of its body. The same run finds all 20 `fast` scripts in the closures plan, `tests/boost_drift_replay.py` among them (`## Raise justification`).
- `PYTHONPATH=tests/hastub python tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 93e6a63d2855651448a2b8f677b392feddc03c99 HEAD`: `Architecture score: dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python tests/closure.py selftest`: `ALL 112 closure shrink pins PASSED`.
- Self-tests:
  - `python3 tools/pr/merge_main_bot.py --self-test`: `40 checks, 0 failed`.
  - `python3 tools/audit/seat/merge_train.py --self-test`: `198 checks, 0 failed`.
  - `python3 tools/audit/seat/record_row.py --self-test`: `all checks passed`.
  - `bash tools/audit/seat/ci-watch.sh --self-test`: `8 checks, 0 failed`.
  - `python3 -I tests/ci_ratchet.py --self-test`: `15 checks, 0 failed`.
- `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`. `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`: `RESULT uncovered_files=0 count`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `tmp_paths: 0 refused, 0 stale allow entries at HEAD, ledger lines added since 93e6a63d2855`.
- Carry 3 (#2529's review): PR G has merged, so main's `selftest_wiring` rule is the wide one. At this head `python3 -I tools/audit/seat/selftest_wiring.py --check` reads `selftest_wiring: 73 self-testing, 73 wired, 0 unwired`, rc 0. That discharges the check owed at the merge that brings PR G in.
- Carry 1 (#2394's Friction): `grep -n -E "GITHUB_TOKEN push (triggers no|leaves no|creates no) pull_request run" .github/workflows/tests.yml .github/workflows/nightly.yml | wc -l` reads `0`.
- `.github/workflows/tests.yml` has 19 job ids (27 at the base `49c222280`) and `nightly.yml` has 6, as the design's totals say. The command is `python3 -c "import yaml; print(len(yaml.safe_load(open('.github/workflows/tests.yml'))['jobs']))"`, and the same for `nightly.yml`.
- `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>` reports its own counts. Run on the round-2 body, it read `1 bad destination(s)` (`R10-CI-LAYOUT is done (resume.stage done)`). This body routes those two items to live groups (`## Red checks`, `## Friction`).
- `env PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>` was run at this head under `/opt/hpo/venv-ci`. Its step lines are its own output, and `closures` is skipped under the env var (CI's `closures` and `closures-autofix` own it).

## Approval

This PR changes policy, so an approving review at the head is owed before merge: the CODEOWNER session's, under mandate 6329234399. The policy files are `dev/governance/rules/ci-autofix.md` and `dev/governance/rules/defect-root-cause.md`, with their generated `.claude/rules/` and `.cursor/rules/` copies (`node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`), and decision 0011's workflow paragraph.

- `ci-autofix.md`'s "`recheck-gate` treats `ci:` as PR-like (not `slow`)" becomes "Every Tests dispatch is PR-like".
- `defect-root-cause.md` adds `nightly.yml` to what `nightly-status` reads, and says to dispatch Nightly rather than Tests.
- Decision 0011's workflow paragraph points at `nightly.yml`, and its "non-recheck" qualifier goes.

The code-owned files are `.github/workflows/tests.yml`, the new `.github/workflows/nightly.yml` and `.github/actions/nightly-ha/action.yml`, `.github/CODEOWNERS` (which gains `/.github/actions/`), and `tests/README.md`. One `*_budgets.json` row rises (`## Raise justification`). Round 3's two files, `tools/pr/ci_predict.py` and `tools/pr/prepr.sh`, are neither code-owned nor policy.

## Raise justification

`tests/ci_budgets.json` `script_runs_per_push` goes from 53 to 54. The reason is in the commit message `abf4f40b7` and in the file's `reason` row. **It is still needed at this head.** Main has not moved the count. Origin/main `93e6a63d2` still records 53 and still carries `tests/composed_closures.json`. Its rule is the closures plan (34) less the one composed script (1) plus the `fast` stage (20). Main's raw enumeration (`closure.test_scripts()` less `SLOW_GATED`, plus `fast`) reads 34 + 20, the same as this head's.

- PR 0 recorded 53 as its every-script-once count: the closures lane's full plan (34), less the one script it consumed from `coverage`'s composed recording, plus the coverage `fast` stage (20).
- W1 removes that composition (owner ruling D-4), so `closures` records `tests/boost_drift_replay.py` bare: one more execution per push. This is the trade the design's section 2(c) prices.
- PR 0 carried this re-record to this PR (roster carry "From PR r10-ci-layout-p0").
- `_cir_once_count()` in `tests/entities.py` derives 54 from the two instruments' own enumerations and pins the budget equal to it. A planted extra run turns the ratchet red, and exactly 54 does not.

Payments tried: four, none taken (listed below). The count is derived, not chosen: `_cir_once_count()` in `tests/entities.py` reads 54 from the two instruments' enumerations. So once W1 removes the composition, a raise is the only sound option.

The four payments, re-examined at this head. All 20 `fast` scripts are also in the closures plan (`## Figures`), so a payment of one run would have to stop one of those 20 being executed twice per push. Each candidate:

1. **Let `closures` consume `coverage`'s recording of `tests/boost_drift_replay.py` again (the 53 state).** This is C1 itself, the alternative owner ruling D-4 refused (V2 in DESIGN-P1 2(c)). It keeps two files, a job, a workflow edge and four `closure.py` entry points that W1 deletes. It was not scored, because the owner's ruling already decides it. Not taken.
2. **Let `closures` consume `coverage`'s recording of a different one of the 20 shared scripts.** This is the same composition mechanism under another name, so the same ruling and the same cost apply. Not taken.
3. **Move `tests/boost_drift_replay.py` to `SLOW_GATED`, so the per-push closures plan drops it.** The per-push scoped gate would lose that script's measured closure, so a diff reaching it would go unselected. That deletes working functionality to fit, which `CLAUDE.md` rule 2 forbids. Not taken.
4. **Drop `tests/boost_drift_replay.py` from `coverage`'s `fast` stage.** This loses its per-push line coverage, which is also deletion. Not taken.

No payment improves the architecture, so the raise stands, under mandate 6329234399's `all` scope. The score was run on this head's diff against its merge base: `score.py --diff 93e6a63d2 HEAD` (`## Figures`).

Architecture score: dS +0.0000 NULL

## Red checks

Read from the check-runs API (`gh api repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs`) for each commit the branch pushed. Commits `2bd0e21b1` and `f2d28782d` carry no check runs; neither was a run head. Superseded runs that concluded `cancelled` are not reds.

- **`31cf0426`:** `instrument-self-tests` 119409742235, `nightly-status` 119409744053, `budget-raise-gate` 119409742323 and 119409761440, and `closures` 119409960810.
- **`bbe90b2dd`** (the `closures-autofix` bot commit): `instrument-self-tests` 119418760342, `nightly-status` 119418770965, `budget-raise-gate` 119439604580, and `pr-contract` 119418760799.
- **`0644c36d4`** (the delivery-row commit): `budget-raise-gate` 119435566119, 119435566980 and 119450310110, and `nightly-status` 119435894694.
- **`e93de8667`** (the bot's main merge): `budget-raise-gate` 119520480162 and 119555482347, and `nightly-status` 119513713274.

Each, answered:

- `instrument-self-tests` (governance.yml, at `31cf0426` and again at `bbe90b2dd`, which carried no fix) **was caused by this PR and is fixed since `e4294cde5`.** Step 23, "Refuse a push that names the host, and an unregistered pusher", failed on `python3 -I tools/audit/seat/ref_privacy.py --check` with `REFUSE .github/workflows/nightly.yml:381: a push site in a file PUSHERS does not name`. The cause: this PR moved three push sites from `tests.yml` to `nightly.yml` and left `PUSHERS` keyed on the old file. Fix `e4294cde5`, mutation M7, null control above. It did not go red at `0644c36d4` or `e93de8667`.
  - **Cheaper detector:** `python3 -I tools/audit/seat/ref_privacy.py --check`, 0.70 s on this seat. Neither `tools/pr/prepr.sh` nor `tests/run.sh` runs it. `prepr.sh` step 3f6 runs its sibling from the same governance job, `tmp_paths.py --check`.
  - **Process state (a):** the process did not exist. This is the second instance in the CI-layout group. #2447's first head went red on this same step, and the roster recorded "not in prepr; the standing cost is one more step there, left to R10-CI-LAYOUT's decision".
  - **Cost test,** per occurrence, in wall-clock:
    - the countermeasure costs 0.70 s per `prepr.sh` run;
    - the defect costs one `instrument-self-tests` run (5 min 35 s, 18:35:40-18:41:15Z), one refused `open_pr.sh` push, and a full fixer round;
    - it recurred in 2 of the CI-layout group's PRs (#2447, #2585).
    - The countermeasure pays for itself.
  - It is a root-cause seat's to build, beside the fix and not inside it (`defect-root-cause.md`): add `ref_privacy.py --check` beside step 3f6's `tmp_paths.py --check`, with a mutant that deletes the step. `R10-CI-LAYOUT` is done, so it goes to the group that owns `tools/pr/prepr.sh`. Carry: R10-PREPR-CAP
- `nightly-status` (at every commit above) **grades main, not this diff.** It runs the base's pinned copy of `tests/nightly_status.py` (`PINNED: 5a755f53e` at `e93de8667`), which reads `tests.yml`. Job 119513713274 printed `NIGHTLY FAILED: mutation-nightly, slow failed last night.` for scheduled run 39563978649 (2026-10-21T07:43:20Z, head `c77f89d`). That is the newest concluded `schedule` run of `tests.yml`, and run 39681119764 was still in flight.
  - `slow` (job 119101702593): `FAIL synthetic-dhw-only.json: cycle_cost [1 offender(s): loop_cpu_ratio 0.1138 over its budget 0.111]`, `1 of 93 replay checks FAILED`. This is the replay cap in `tests/replay.py`. Carry: R10-REPLAY-CAP
  - `mutation-nightly` (job 119101702662), step "Drive the table over the whole package": `10 survivor(s) of 23 evaluated = 39.1% ... cap 30.0%`, `MUTATION TABLE BREACHED`. This is the nightly sample over `custom_components/`, which this diff does not touch. No roster group owns that survivor rate, and the first post-merge Nightly dispatch re-grades it (Forward-carry). Carry: R10-CI-LAYOUT-P2
  - **Does this diff touch its inputs?** It touches its workflow input, not any step those jobs run. `slow|` and `mutation-nightly|` change only in their job rows in the static map (`if:` and `needs:`), and no file under `custom_components/` or `tests/replay.py` is in the diff.
  - **Does it change what nightly-status reads?** Yes, but only after the merge. Main's `nightly_status.py` `DEFAULT_WORKFLOW` becomes `nightly.yml`, so post-merge PRs grade the newest `nightly.yml` schedule-or-dispatch run instead of `tests.yml`'s. The lane set (`REQUIRED_LANES`) is unchanged, and so is the pinned-grader mechanism. Until a `nightly.yml` run concludes on main, `nightly-status` reads RUNNING or ABSENT (risk R-4, Forward-carry).
  - **Cheaper detector:** none for this PR. The failing lanes are main's, and no check on this diff runs them.
- `budget-raise-gate` (at every commit above): `RAISE tests/ci_budgets.json: script_runs_per_push: 53 -> 54 (a cap went up)`. At `31cf0426` it refused for want of a decisive review by tvofi. At `0644c36d4` (119450310110) it refused with the same words plus `review 5605414779: mandate 6319294694 was revoked by tvofi's comment 6322712314`. The newest run at `e93de8667` (119555482347, 2026-10-21T23:57Z) refused with `REFUSED: a mandated approval is on this head, but ## Raise justification lacks a Payments tried: line; review 5605414779: mandate 6319294694 was revoked by tvofi's comment 6322712314`. Two causes, each answered:
  - The `Payments tried:` line is in this body's `## Raise justification`. The body on the PR at that run was the round-2 body before its last edit, which was never applied.
  - Comment 6322712314 revokes decision 0012, not the mandate. The gate's `MANDATE_REVOKED` is deliberately loose: any owner comment naming the id beside a form of "revoke" voids it. The owner's comment 6329234399 (2026-10-21T23:56:29Z) grants mandate 6329234399 with the same scope and end and names that misreading. This body cites the new id. A mandated approval at this head, citing 6329234399, is the orchestrator's.
  - The guard against a repeat is already a roster group. Carry: R10-FLY-MANDATE-REVOKE-GUARD
  - **Cheaper detector:** none. The gate's input is a review that can exist only after the push.
- `pr-contract` (job 119418760799, at `bbe90b2dd`) failed on the body then on the PR, the round-1 body: `ERROR [pr-body] /tmp/pr-body.md: check instrument-self-tests is red and ## Red checks does not name it`. That body predated the round-2 red. This body names and answers `instrument-self-tests` above, and `pr-contract` was `success` at `e93de8667` (119513739210). **Cheaper detector:** `prepr.sh`'s `ancestry reds` step, which reads the same red history before a push.
- `closures` (119409960810, at `31cf0426`) printed `UNDER-SCOPED`, as expected for a FULL run whose `tests/entities.py` closure gains `nightly.yml` and the action. `closures-autofix` pushed `bbe90b2dd` from the Linux recording, and the head carries it. Both `closures` runs at `e93de8667` are `success`.
- **Round 3's red was predicted, never pushed.** It was `prepr.sh` step 6d's refusal, answered under the summary above. Its cheaper detector is the predictor itself, which ran before any push. The defect was a false positive in that detector, and `188c5728b` fixes it with a pinned arm (M8).

## Forward-carry

- After this merge, dispatch `gh workflow run nightly.yml --ref main` right away. `nightly-status` on PRs based before the merge reads ABSENT once `tests.yml`'s last schedule run ages past two nights. On PRs based after it, it reads RUNNING until that dispatch concludes (DESIGN-P1 risk R-4). The same dispatch is the first re-grade of main's `mutation-nightly` survivor rate (39.1% against 30.0% at run 39563978649). The ledger and record-writer environments' first run under `nightly.yml` is also post-merge (R-3). Carry: R10-CI-LAYOUT-P2
- The runtime half of the null control's pin-chain and nightly rows, and W1's critical-path gain, are measured on post-merge runs only.
  - Pin chain: the next PR whose `mutation` refuses must show `mutation-pins` expanding from `needs.mutation.outputs.shards`.
  - W1 gain: `critpath.py`'s model figures are 8.8 min median on scoped runs and 18.1 min on FULL runs.
  - PR 2's unit runs must re-take both before the umbrella builds on them. Carry: R10-CI-LAYOUT-P2
- `coverage`'s step "Check the restored coverage is main's push run's" stays, against DESIGN-P1 2(a)'s deletion. It executed on 53 of the 84 sampled PR runs that had the step (the deviation note above). PR 2's unit that moves `coverage` must keep it. Carry: R10-CI-LAYOUT-P2
- `fast`'s two warm-cache steps keep a `github.event_name == 'schedule'` arm. It is dead now that `tests.yml` has no schedule (`fast` never ran on one anyway). This PR leaves those steps untouched, because they are outside the design's map. The umbrella's split of `fast` should drop the arm. Carry: R10-CI-LAYOUT-P2
- A job moved between workflow files carries its push sites with it, and `ref_privacy.py`'s `PUSHERS` is keyed on the file. PR 2's move of `tests.yml` into the umbrella must re-key `tests.yml`'s entry in the same diff, and run `python3 -I tools/audit/seat/ref_privacy.py --check` before pushing. Carry: R10-CI-LAYOUT-P2
- PR 2 moves `tests.yml` jobs again, so `prepr.sh` step 6d will run over its diff too. A predicted `INERT READS` is classified only after the read is shown to be a Python process's, as round 3 did. `--apply-inert` on an unverified prediction writes a classification CI never records. `tests/closures.json` still lists five non-INERT files under `inert_reads["tests/entities.py"]`, and `closure.py prune` drops only missing files. The predictor now ignores those five, so they mislead no prediction. Carry: R10-CI-LAYOUT-P2
- `R10-REPLAY-LANE`'s roster `files` names `.github/workflows/nightly.yml`, which this PR creates. Its fixer edits the moved `slow` job there, not in `tests.yml`. Carry: R10-REPLAY-LANE

## Friction

- finding-propagation: unclear: the brief names "the plan addendum A1-A6 / B1-B9 ... find them on the same refs", but neither the design tags nor the roster, the flow-study branch or issue #2495 carries the addendum text. B9 was built from the brief's own sentence ("B9's producer check on the merge_group and recheck events after recheck-gate moves"), and nothing else from the addendum binds PR 1. Carry: R10-CI-LAYOUT-P2
- fixer: cost: CI's job logs and artifacts live on a blob host this cloud seat's proxy refuses. `gh api .../actions/jobs/<id>/logs` and `.../artifacts/<id>/zip` fail with `Forbidden` on the `productionresultssa*.blob.core.windows.net` redirect. So the reds were read through the MCP log reader, one job's tail at a time, and `closures`' recording artifact could not be read. A seat with `gh` logs runs `critpath_fetch.sh` as committed. Carry: R10-CI-LAYOUT-P2
- fixer: cost: governance's `run:` steps write to `$RUNNER_TEMP`, so re-running a skipped step locally from its own text fails (`tee` onto `/sr-self-test.txt`) until `RUNNER_TEMP` is set. A seat replaying a governance job's steps sets it first. Carry: R10-RCA-FRICTION
- fixer: cost: the seat's default `python3` is 3.11, and `tests/entities.py` does not parse there (an f-string `SyntaxError`). The venv at `/opt/hpo/venv-ci` must be first on `PATH`, because the script's children call `python3` by name. Carry: R10-RCA-FRICTION

