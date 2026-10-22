R10-CI-LAYOUT PR 1: the nightly lanes leave tests.yml, the pin plan folds into mutation, recheck-gate goes, and W1 removes the C1 composition at its source

Part of #2495 and of #201. Group: R10-CI-LAYOUT-P1 (roster `handoff/audit-r10-roster`), PR 1 of the four-PR CI-layout sequence. PR 0 merged as #2464; PR G (#2529) is open and orders before this one at merge only. The design is phase 1 of `probe/design-ci-rev4` (`1371a0a6`, archived as the tag `archive/probe/design-ci-rev4`), approved at review round 5 (`archive/probe/design-ci-review5`, `afc00bfe`). This PR builds DESIGN-P1 less step 5b, which PR 0 landed. It includes W1 and B9's producer check.

**Owner gate.** This PR is code-owned CI workflows (`/.github/workflows/`, and `/.github/actions/`, which this PR adds to CODEOWNERS) and policy (`dev/governance/rules/ci-autofix.md`, `defect-root-cause.md`, their `rules_sync` outputs, and decision 0011's workflow paragraph). It also raises one row of `tests/ci_budgets.json` (see `## Raise justification`). The CODEOWNER session approves it at its merged head under mandate 6319294694. No required context is added, renamed or removed.

**Round 2 (this head).** `instrument-self-tests` was red at `31cf0426`. Its step "Refuse a push that names the host, and an unregistered pusher" failed on `ref_privacy.py --check`: `REFUSE .github/workflows/nightly.yml:381: a push site in a file PUSHERS does not name`. This PR moved the nightly-kills push onto main, and `record-autofix`'s two pushes onto `record/autofix`, out of `tests.yml` and into `nightly.yml`. It did not move their `PUSHERS` entry with them. Commit `e4294cde5` registers `nightly.yml` as `republishes`, with the record/autofix-and-main reason. `tests.yml`'s entry keeps only the pull-request-branch reason, since its three remaining push sites are `closures-autofix`, `claims-autofix` and `mutation-autofix`, which all push onto the pull request's own branch. Merge `2bd0e21b1` then brings in the `closures-autofix` bot's `ci: re-record closures` (`bbe90b2dd`), which was already on the pull request branch.

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
  - `CODEOWNERS` gains `/.github/actions/`; `tests/README.md` and `HANDOVER.md` are updated.
  - `r10_replay_loopnorm.py` reads `slow` from both workflow files.
- **Carried in:** the four stale "a GITHUB_TOKEN push leaves no pull_request run" comments in `tests.yml` (#2394's Friction) now state the measured fact: a bot head's runs are created, held `action_required`, and approved by hpo-runs.

**Deviation from the design, with its evidence.** DESIGN-P1 2(a) deletes `coverage`'s step "Check the restored coverage is main's push run's". Its premise is that the step "executed on the schedule run only" (section 0, item 5). At this base the premise is false.

- The step gates per-script coverage reuse (`W5P_REUSE`) on every pull request with a cache hit, and `entities.py`'s `_cov_steps` pins it.
- Over the 90 PR runs in the critical-path fetch below whose four lanes concluded, the step executed 53 times and was skipped 31 times. The count reads the saved `tests_jobs_<run>.json`'s `coverage` steps by name.

So it is kept. Deleting it would let an unverified cache entry stand in for the base's measurement. The step is not on the static map's drop list, and the static check below passes with it kept.

## Head

`2bd0e21b13d3c29795a5f2cba59f14ccf7ff2105`, committed 2026-10-21T18:59:57Z. It is the reviewed PR head `31cf0426` (code `1b4fae9df` merged with origin/main `57f0c9c77`) plus two parents' worth of change:

- `e4294cde5`, the round-2 fix in `tools/audit/seat/ref_privacy.py`;
- the bot commit `bbe90b2dd` (`ci: re-record closures`, `tests/closures.json` only), merged in without a conflict.

`git diff --stat 31cf0426 HEAD` reads `tests/closures.json | 7 +++++++` and `tools/audit/seat/ref_privacy.py | 4 +++-`. `git merge-base HEAD origin/main` is `57f0c9c77cfd5958e0a2443e158bea8326bedae2`. That is origin/main's tip, read at 2026-10-21T19:00:15Z, so the branch is 0 commits behind.

Unless a figure says otherwise, it was re-taken at this head, or at `e4294cde5` where it says so. Every local figure was taken on a Linux cloud seat under `/opt/hpo/venv-ci` (CPython 3.14.7). The critical-path figures and the coverage-step count come from the round-1 CI fetch and are dated there.

The PR head is `e93de8667`, a bot main-merge (`ci: merge main`) of this handoff head with main's #2529 and later merges. It carries no code of this handoff's own, so every figure in this body is the one at the head named above.

## Mutation proof

Round 2's fix:

- **M7.** Delete `nightly.yml`'s two-line `PUSHERS` entry in a throwaway detached worktree at this head (`git diff --stat`: `1 file changed, 2 deletions(-)`), then run `python3 -I tools/audit/seat/ref_privacy.py --check`. It goes red with `REFUSE .github/workflows/nightly.yml:381: a push site in a file PUSHERS does not name: ...` and `1 refused`, rc 1. This is the check governance's `instrument-self-tests` runs, and the same refusal it printed at `31cf0426`.
- `ref_privacy.py`'s recorded closure is `tests/entities.py`'s alone (`tests/closures.json`). Under M7, `entities.py` still passes (`## Figures`, "M7's closure run"), so the governance step is M7's only killer.
- **The reason text is unpinned, by the registry's design.** Restoring `tests.yml`'s old wording ("record/autofix or main (nightly kills)") still reads `0 refused`, rc 0, at `e4294cde5`. `registry_refusals` keys on the path and on `guarded` versus a reason, never on the reason's words. So the wording change is prose. M7 is the mutant that removes the predicate's input.

Round 1's mutants were taken at `eb804069e`. That tree differs from this head's in `c1_consumers.sh`, `tests/closures.json` and `ref_privacy.py`, none of which these mutants touch. Six production elements were reverted to their base form at once, in a throwaway detached worktree. Each mutant touches a different artifact, so each failing check names its own mutant. The full run read `6 of 2387 ENTITY CHECKS FAILED`, exactly these:

- M1 (B9): `briefs`' dispatch arm restored to `(workflow_dispatch && needs.recheck-gate.outputs.recheck == 'true')` → `every required context tests.yml produces runs on an autofix or batch-proof dispatch (B9)`.
- M2 (b): `if: always()` deleted from `mutation`'s plan step → `the pin shard count scales with the diff's new sites ... (plan wiring=False)`.
- M3 (W1): `closures` given `needs: [closure-scope, coverage]` again → `the C1 composition stays removed at its source (W1)`.
- M4 (a): `nightly_status.DEFAULT_WORKFLOW` back to `tests.yml` → `the reporter watches exactly the lanes a pull request cannot see`.
- M5 (a): `nightly.yml`'s `nightly-ha` no longer calls the action → `both nightly-ha arms check out, then run the shared composite action on their matrix image`.
- M6 (a): `mutation-ledger`'s main ref guard deleted → `a branch-ref dispatch reaches neither mutation-ledger nor mutation-ledger-push; ...`.

Self-test mutants, each in a second throwaway worktree and restored:

- `PIN_CHAIN` given `mutation-pin-plan` back: `merge_main_bot self-test: 40 checks, 1 failed`. The failing check is "while mutation runs ... the retired mutation-pin-plan name is no chain job".
- `nightly.yml`'s `record-autofix` renamed: `orchestrator_tick self-test: 172 checks, 2 failed` (`MAIN D-1`: the push-run jobs are exactly the record beat, and its red is named).

The static null control's own plant is under `## Null control`.

## Null control

- **Round 2's.** The unmodified PR head `31cf0426`: `python3 -I tools/audit/seat/ref_privacy.py --check` prints `20 file(s) with a push site, 9 guarded, 991 line(s) added since 57f0c9c77cfd judged, 1 refused`, rc 1. This head prints `0 refused`, rc 0 (`## Figures`). Its self-test `ref_privacy self-test: 66 checks, 0 failed` is unchanged.
- The unmutated head: `ALL 2388 ENTITY CHECKS PASSED` (`PYTHONPATH=tests/hastub python tests/entities.py`, at `e4294cde5`; this head's run is under `## Figures`). Round 1 read `ALL 2387` at `eb804069e` and `ALL 2375` at the base `49c222280`. Main's newer checks make up the difference; this round adds none.
- The **static** half of the design's null control (DESIGN-P1 section 4, `measure/rev/unitcheck2.py static`) uses a closed map, committed as `dev/audit/harnesses/r10_ci_layout_p1/unitcheck_map.json`.
  - Head: `STATIC rows 225->232 lost 0 gained 0 changed 29 (mapped 29) misplaced 0 rc 0`.
  - Planted: deleting one step from `nightly.yml`'s `record-autofix` (a verbatim move must keep it) gives `STATIC rows 225->231 lost 1 gained 0 changed 29 (mapped 29) misplaced 0 rc 1  (1 LOST row(s))`.
  - Each admitted `changed` row is printed before and after by the same run.
  - `record-autofix` and `mutation-ledger-push` show no row at all: they moved verbatim.
- The **runtime** half (DESIGN-P1 section 4's table) needs this PR's own CI runs and post-merge runs, so it is the orchestrator's. Its pairs are unchanged from the design. The `nightly` and `pin chain` rows are checked after the merge (risks R-2, R-4).
- The critical-path harness's self-test `edge+tail gain 330 s (want 330) ok; null control 0 s (want 0) ok`. The null control is a run whose `closures` already ends before `coverage`.

## Figures

- `python3 -I tools/audit/seat/ref_privacy.py --check`, at this head: `ref_privacy --check at HEAD: 20 file(s) with a push site, 9 guarded, 1001 line(s) added since 57f0c9c77cfd judged, 0 refused`, rc 0. It printed `1 refused` (the nightly.yml:381 line) at `31cf0426`, and the same under M7.
- `python3 -I tools/audit/seat/ref_privacy.py --self-test`: `ref_privacy self-test: 66 checks, 0 failed`.
- **The class, round 2.** The rule that enumerates the seams is `ref_privacy.sites(ref_privacy.grep("HEAD"))` checked by `registry_refusals`, which is what `--check` runs. Every push site under `tools/`, `.claude/workflows/` and `.github/workflows/` (20 files) gets a registry verdict, so no moved push site is unjudged. The two files this PR changes the push sites of:
  - `tests.yml`, sites at lines 2344, 2616 and 2904 (`closures-autofix`, `claims-autofix`, `mutation-autofix`): already registered, reason narrowed in this diff;
  - `nightly.yml`, sites at lines 381, 746 and 867 (`mutation-ledger-push`, `record-autofix` twice): registered in this diff.
- **The wider class: a path-keyed registry that names `tests.yml` and now owes `nightly.yml`.** The command was `git grep -l -E "workflows/tests\.yml" -- tools tests .claude/workflows .github ':!dev'`, with each file's `nightly.yml` count beside it. It returns 19 files.
  - 7 already name `nightly.yml`: `tests.yml`, `tests/README.md`, `closure.py`, `entities.py`, `merge_train.py`, `ref_privacy.py` (this round) and `policy_lint.mjs`.
  - `tests/closures.json` names it since the bot's re-record.
  - The other 11 read `tests.yml` for what stays there, so each is already right:
    - fixtures: `card.mjs`, `lane_skip.py`, `budget_raise_gate.py`, `contract_rerun.py`, `stamp.py`;
    - comments: `run.sh`, `stress.py`;
    - the pull-request dispatch arms: `a1_dispatch_arms.sh`;
    - `pull_request` autofix runs: `autofix_statuses.sh`;
    - the job count `counts.mjs` publishes as `tests.yml`'s own;
    - `PIN_CHAIN`'s three `tests.yml` jobs: `merge_main_bot.py`.
- Governance's `instrument-self-tests` steps that the red step skipped at `31cf0426` were each re-run here from `governance.yml`'s own `run:` text, at `e4294cde5`, with `RUNNER_TEMP` set to a temp directory:
  - `sweep_render self-test: 21 checks, 0 failed`; `policy_reread_check self-test: 15 checks, 0 failed`;
  - `orchestrator_tick self-test: 172 checks, 0 failed`;
  - `selftest_wiring: 38 self-testing, 38 wired, 0 unwired`;
  - `throwaway_git: 0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`;
  - `merge_train self-test: 198 checks, 0 failed`; `queue_pre_flight self-test: 41 checks, 0 failed`;
  - `train.sh self-test: ok (5 refusals shown, root and options reach the child, no unasked flag)`.
- M7's closure run, `PYTHONPATH=tests/hastub python tests/entities.py` in the mutant worktree: `ALL 2388 ENTITY CHECKS PASSED`, rc 0. So `entities.py` does not kill M7, and governance's `ref_privacy.py --check` step is its killer, as `## Mutation proof` says. The `FAIL` lines in that run's output are its self-test fixtures' planted negatives, and the same lines print at the unmutated head.
- `PYTHONPATH=tests/hastub python tests/entities.py`, at this head: `ALL 2388 ENTITY CHECKS PASSED`, rc 0.
- `python3 -I tools/audit/seat/ref_privacy.py --check` takes 0.67 s here: `date +%s.%N` either side of the run, at `e4294cde5`. This is the cost under `## Red checks`.
- `python3 -I dev/audit/harnesses/r10_ci_layout_p1/critpath.py RAW CASES --case SCOPED --n 20` (round 1): `SCOPED: runs 20; wall median 34.9 min; W1 gain median 8.8 min, min 0.0, max 14.4; runs gaining > 0: 19`.
  - The method is the design's phase-2 critical-path counterfactual (the `critpath` measure on the archived design tag). Every job's duration is held fixed; `closures` starts its measured queue after `closure-scope` instead of after `coverage`; `composed-proof` adds no tail.
  - The input is the 20 newest completed `pull_request` runs of `tests.yml` whose `closure-scope` log reads `CASE: SCOPED`, out of the 37 newest whose four lanes concluded, read 2026-10-21 by `dev/audit/harnesses/r10_ci_layout_p1/critpath_fetch.sh`.
  - On this seat the logs came through the MCP log reader, because the proxy refuses the log blob host.
- The same with `--case FULL` (round 1): `FULL: runs 13; wall median 63.8 min; W1 gain median 18.1 min, min 0.0, max 35.6; runs gaining > 0: 11`. All 13 FULL cases name a gate file: `tests/closures.json` 7, `tests/closure.py` 4, `tests/requirements-ci.txt` 1, `.github/workflows/tests.yml` 1.
- **The flow study's claim, corrected.** The model says W1 removes "about 7 min on a FULL-scope train and 19-21 min on a scoped run". Measured on these runs, the ordering is the reverse: a scoped run's median gain is 8.8 min and a FULL run's is 18.1 min. On a FULL run `closures` re-records everything and waited for `coverage`'s whole traced suite; on a scoped run it re-records little and `fast` more often ends the run. Both figures are the design's model over measured job times, not a measured post-W1 run. The post-merge runs are the check.
- `sh dev/audit/harnesses/r10_ci_layout_p1/unitcheck.sh`, at this head: `head:    STATIC rows 225->232 lost 0 gained 0 changed 29 (mapped 29) misplaced 0 rc 0`, `plant:   STATIC rows 225->231 lost 1 gained 0 changed 29 (mapped 29) misplaced 0 rc 1  (1 LOST row(s))` (Null control above).
- `sh dev/audit/harnesses/r10_ci_layout_p1/c1_consumers.sh HEAD` (the design's own C1 census, read from `archive/probe/design-ci-rev4`), at this head: its `--- files:` list names 6 files, none under `.github/`, `tools/coverage/` or `tests/` except `tests/entities.py`, whose hits are the no-C1-token pin's own pattern. Each file's disposition:
  - `merge_train.py` and `orchestrator_tick.py`: the design's kept fixtures (`composed-proof` as a never-concluding lane);
  - `dev/audit/harnesses/r10_carry_sweep_rows.py`: a round record naming the old job;
  - `dev/audit/harnesses/r10_ci_layout_p1/critpath.py` and `unitcheck_map.json`: this PR's measurement, which must name the deleted job to model it;
  - `tests/entities.py`: the pin.
  - At `origin/main` (`57f0c9c77`) the same command lists 12 files.
- `PYTHONPATH=tests/hastub python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`, at `e4294cde5`: `MODE: FULL -- every test script runs, nothing is scoped out.`, reason `.github/actions/nightly-ha/action.yml changes the gate itself, so every closure is suspect`. A gate file, as the design says. The CI `closures` FULL arm and `closures-autofix` own the re-recording; the latter already pushed `bbe90b2dd`, merged here.
- `python3 tests/closure.py prune` (round 1, before its commit): `pruned 3 phantom entry(ies)`: the deleted allow-list and proof driver in `tests/entities.py`'s closure (2) and its inert reads (1).
- The every-script-once count at `e4294cde5` is 54. `closure.test_scripts()` less `SLOW_GATED` is 34, and coverage_tree.sh's `fast` stage, run by bash, is 20. This is `_cir_once_count()` in `tests/entities.py`, pinned equal to the budget row. The same run lists the scripts in both enumerations: all 20 `fast` scripts, `tests/boost_drift_replay.py` among them (`## Raise justification`).
- `PYTHONPATH=tests/hastub python tests/structure.py`, at this head: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 57f0c9c77cfd5958e0a2443e158bea8326bedae2 HEAD`, at `e4294cde5`: `Architecture score: dS +0.0000 NULL`. The bot commit merged after it touches only `tests/closures.json`, which the score does not read.
- `PYTHONPATH=tests/hastub python tests/closure.py selftest`, at `e4294cde5`: `ALL 112 closure shrink pins PASSED`. At the old base `49c222280` it read `ALL 124`; the 12 removed pins were C1's.
- Self-tests, at `e4294cde5`:
  - `python3 tools/pr/merge_main_bot.py --self-test`: `40 checks, 0 failed`.
  - `python3 tools/audit/seat/orchestrator_tick.py --self-test`: `172 checks, 0 failed`, against `168` at the base; the four new checks are `MAIN D-1`.
  - `python3 tools/audit/seat/merge_train.py --self-test`: `198 checks, 0 failed`.
  - `python3 tools/audit/seat/record_row.py --self-test`: `all checks passed`.
  - `bash tools/audit/seat/ci-watch.sh --self-test`: `8 checks, 0 failed`.
  - `python3 -I tests/ci_ratchet.py --self-test`: `15 checks, 0 failed`.
- `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py`, at `e4294cde5`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `node tools/policy/policy_lint.mjs`, at this head: `TOTAL: 0 error(s) across 41 policy file(s)`. `node tools/policy/rules_sync.mjs --check`, at `e4294cde5`: `RULES-SYNC ok`.
- `python3 dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`, at `e4294cde5`: `RESULT uncovered_files=0 count`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`, at this head: `tmp_paths: 0 refused, 0 stale allow entries at HEAD, ledger lines added since 57f0c9c77cfd`
- Carry 3 (#2529's review): `python3 -I tools/audit/seat/selftest_wiring.py --check`, at this head: `selftest_wiring: 38 self-testing, 38 wired, 0 unwired`, rc 0. PR G has not merged, so main's rule is still the narrow one. The check is owed again at the merge that brings PR G in.
- Carry 1 (#2394's Friction): `grep -n -E "GITHUB_TOKEN push (triggers no|leaves no|creates no) pull_request run" .github/workflows/tests.yml .github/workflows/nightly.yml` prints nothing (`| wc -l`: `0`, at `e4294cde5`).
- `env PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>`, at this head under `/opt/hpo/venv-ci`: `PRE-PR: 2bd0e21b13d3c29795a5f2cba59f14ccf7ff2105 00000000000000000000000000000`, rc 0, `MODE: FULL`, `closures` skipped under the env var (CI's `closures` and `closures-autofix` own it). Its `ancestry reds` step read `the body answers every red this branch pushed (budget-raise-gate closures instrument-self-tests nightly-status)`, and its figures step is the figure linter over this body. The body's only edit after that run is this line.
- `.github/workflows/tests.yml` has 19 job ids (27 at the base) and `nightly.yml` has 6, as the design's totals say. The command is `python3 -c "import yaml; print(len(yaml.safe_load(open('.github/workflows/tests.yml'))['jobs']))"`, and the same for `nightly.yml`.

## Approval

This PR changes policy, so an approving review at the head is owed before merge: the CODEOWNER session's, under mandate 6319294694. The policy files are `dev/governance/rules/ci-autofix.md` and `dev/governance/rules/defect-root-cause.md`, with their generated `.claude/rules/` and `.cursor/rules/` copies (`node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`), and decision 0011's workflow paragraph.

- `ci-autofix.md`'s "`recheck-gate` treats `ci:` as PR-like (not `slow`)" becomes "Every Tests dispatch is PR-like".
- `defect-root-cause.md` adds `nightly.yml` to what `nightly-status` reads, and says to dispatch Nightly rather than Tests.
- Decision 0011's workflow paragraph points at `nightly.yml`, and its "non-recheck" qualifier goes.

The code-owned files are `.github/workflows/tests.yml`, the new `.github/workflows/nightly.yml` and `.github/actions/nightly-ha/action.yml`, `.github/CODEOWNERS` (which gains `/.github/actions/`), and `tests/README.md`. One `*_budgets.json` row rises (`## Raise justification`).

## Raise justification

`tests/ci_budgets.json` `script_runs_per_push` goes from 53 to 54. The reason is in the commit message `abf4f40b7` and in the file's `reason` row.

- PR 0 recorded 53 as its every-script-once count: the closures lane's full plan (34), less the one script it consumed from `coverage`'s composed recording, plus the coverage `fast` stage (20).
- W1 removes that composition (owner ruling D-4), so `closures` records `tests/boost_drift_replay.py` bare: one more execution per push. This is the trade the design's section 2(c) prices.
- PR 0 carried this re-record to this PR (roster carry "From PR r10-ci-layout-p0").
- `_cir_once_count()` in `tests/entities.py` derives 54 from the two instruments' own enumerations and pins the budget equal to it. A planted extra run turns the ratchet red, and exactly 54 does not.

Payments tried: four, none taken (listed below); the count is derived, not chosen (`_cir_once_count()` in `tests/entities.py` reads 54 from the two instruments' enumerations), so a raise is the only sound option once W1 removes the composition.

The four payments, re-examined at `e4294cde5`. All 20 `fast` scripts are also in the closures plan (`## Figures`), so a payment of one run would have to stop one of those 20 being executed twice per push. Each candidate:

1. **Let `closures` consume `coverage`'s recording of `tests/boost_drift_replay.py` again (the 53 state).** This is C1 itself: owner ruling D-4's refused alternative (V2 in DESIGN-P1 2(c)). It keeps two files, a job, a workflow edge and four `closure.py` entry points that W1 deletes. It was not scored, because the owner's ruling already decides it. Not taken.
2. **Let `closures` consume `coverage`'s recording of a different one of the 20 shared scripts.** This is the same composition mechanism under another name, so the same ruling and the same cost apply. Not taken.
3. **Move `tests/boost_drift_replay.py` to `SLOW_GATED`, so the per-push closures plan drops it.** The per-push scoped gate would lose that script's measured closure, so a diff reaching it would go unselected. That deletes working functionality to fit, which `CLAUDE.md` rule 2 forbids. Not taken.
4. **Drop `tests/boost_drift_replay.py` from `coverage`'s `fast` stage.** This loses its per-push line coverage, which is also deletion. Not taken.

No payment improves the architecture, so the raise stands, under mandate 6319294694's `budget-raise` scope. The score was run on the diff before and after the round-2 commit: `score.py --diff 57f0c9c77 HEAD` at `e4294cde5` (`## Figures`).

Architecture score: dS +0.0000 NULL

## Red checks

The reds on this branch's pushed commits are `instrument-self-tests`, `nightly-status` and `budget-raise-gate`, check-runs 119409742235, 119409744053 and 119409761440 of head `31cf0426`, read with the MCP job-log reader.

- `instrument-self-tests` (governance.yml, job 119409742235) **was caused by this PR, and is fixed at this head.** Step 23, "Refuse a push that names the host, and an unregistered pusher", failed on `python3 -I tools/audit/seat/ref_privacy.py --check` with `REFUSE .github/workflows/nightly.yml:381: a push site in a file PUSHERS does not name`. That was reproduced at `31cf0426` (rc 1). The cause: this PR moved three push sites from `tests.yml` to `nightly.yml` and left `PUSHERS` keyed on the old file. Fix `e4294cde5`, mutation M7, null control above. Steps 24-26 and 55-58, which the failure skipped, were run here and pass (`## Figures`).
  - **Cheaper detector:** `python3 -I tools/audit/seat/ref_privacy.py --check`, 0.67 s on this seat. Neither `tools/pr/prepr.sh` nor `tests/run.sh` runs it: `git grep -n ref_privacy -- tools/pr/prepr.sh` prints nothing. `prepr.sh` step 3f6 runs its sibling from the same governance job, `tmp_paths.py --check`.
  - **Process state (a):** the process did not exist. This is the second instance in this group. #2447's first head went red on this same step, and the roster recorded "not in prepr; the standing cost is one more step there, left to R10-CI-LAYOUT's decision".
  - **Cost test,** per occurrence, in wall-clock:
    - the countermeasure costs 0.67 s per `prepr.sh` run;
    - the defect costs one `instrument-self-tests` run (5 min 35 s, 18:35:40-18:41:15Z), one refused `open_pr.sh` push, and a full fixer round;
    - it recurred in 2 of this group's PRs (#2447, #2585).
    - The countermeasure pays for itself.
  - It is a root-cause seat's to build, beside the fix and not inside it (`defect-root-cause.md`). It goes to the group that already holds the first instance: add `ref_privacy.py --check` beside step 3f6's `tmp_paths.py --check`, with a mutant that deletes the step. Carry: R10-CI-LAYOUT
- `nightly-status` (job 119409744053) **grades main, not this diff.** At this PR it runs main's pinned copy of `tests/nightly_status.py` (`PINNED: 57f0c9c77`, which reads `tests.yml`). It reported `NIGHTLY FAILED: mutation-nightly, slow failed last night`, for scheduled run 39563978649 (2026-10-21T07:43:20Z, head `c77f89d`). That is the newest `schedule` run of `tests.yml`; the one before it, 39387919507, also concluded `failure`.
  - `slow` (job 119101702593): `FAIL synthetic-dhw-only.json: cycle_cost [1 offender(s): loop_cpu_ratio 0.1138 over its budget 0.111]`, `1 of 93 replay checks FAILED`. This is the replay cap in `tests/replay.py`. Carry: R10-REPLAY-CAP
  - `mutation-nightly` (job 119101702662), step "Drive the table over the whole package": `10 survivor(s) of 23 evaluated = 39.1% ... cap 30.0%`, `MUTATION TABLE BREACHED`. This is the nightly sample over `custom_components/`, which this diff does not touch. No roster group owns that survivor rate; the first post-merge Nightly dispatch re-grades it (Forward-carry). Carry: R10-CI-LAYOUT-P2
  - **Does this diff touch its inputs?** It touches its workflow input, not any step those jobs run. `slow|` and `mutation-nightly|` change only in their job rows in the static map (`if:` and `needs:`), and no file under `custom_components/` or `tests/replay.py` is in the diff.
  - **Does it change what nightly-status reads?** Yes, after the merge only. Main's `nightly_status.py` `DEFAULT_WORKFLOW` becomes `nightly.yml`, so post-merge PRs grade the newest `nightly.yml` schedule-or-dispatch run instead of `tests.yml`'s. The lane set (`REQUIRED_LANES`) is unchanged, and so is the pinned-grader mechanism. On this PR's own runs nothing changes, because the job restores the base's copy. Until a `nightly.yml` run concludes on main, `nightly-status` reads RUNNING or ABSENT (risk R-4, Forward-carry).
  - **Cheaper detector:** none for this PR. The failing lanes are main's, and no check on this diff runs them.
- `budget-raise-gate` (job 119409761440): `RAISE tests/ci_budgets.json: script_runs_per_push: 53 -> 54 (a cap went up)`, `REFUSED: no decisive review by tvofi (id 70032254) on this pull request`. This is red by design until the raise is approved at its head. The orchestrator approves under mandate 6319294694 against `## Raise justification` above, which records each payment tried and the `Architecture score: dS` line. **Cheaper detector:** none. The gate's only input is a review that can exist only after the push.
- `closures` printed `UNDER-SCOPED` at `31cf0426`, as expected for a FULL run whose `tests/entities.py` closure gains `nightly.yml` and the action. `closures-autofix` pushed `bbe90b2dd` from the Linux recording, and this head merges it. No seat ran `derive_closures.sh` here (`PREPR_SKIP_CLOSURES=1`).

## Forward-carry

- After this merge, dispatch `gh workflow run nightly.yml --ref main` right away. `nightly-status` on PRs based before the merge reads ABSENT once `tests.yml`'s last schedule run ages past two nights. On PRs based after it, it reads RUNNING until that dispatch concludes (DESIGN-P1 risk R-4). The same dispatch is the first re-grade of main's `mutation-nightly` survivor rate (39.1% against 30.0% at run 39563978649). The ledger and record-writer environments' first run under `nightly.yml` is also post-merge (R-3). Carry: R10-CI-LAYOUT-P2
- The runtime half of the null control's pin-chain and nightly rows, and W1's critical-path gain, are measured on post-merge runs only.
  - Pin chain: the next PR whose `mutation` refuses must show `mutation-pins` expanding from `needs.mutation.outputs.shards`.
  - W1 gain: `critpath.py`'s model figures are 8.8 min median on scoped runs and 18.1 min on FULL runs.
  - PR 2's unit runs must re-take both before the umbrella builds on them. Carry: R10-CI-LAYOUT-P2
- `coverage`'s step "Check the restored coverage is main's push run's" stays, against DESIGN-P1 2(a)'s deletion. It executed on 53 of the 84 sampled PR runs that had the step (see the body's deviation note). PR 2's unit that moves `coverage` must keep it. Carry: R10-CI-LAYOUT-P2
- `fast`'s two warm-cache steps keep a `github.event_name == 'schedule'` arm. It is dead now that `tests.yml` has no schedule (`fast` never ran on one anyway). This PR leaves those steps untouched, because they are outside the design's map. The umbrella's split of `fast` should drop the arm. Carry: R10-CI-LAYOUT-P2
- A job moved between workflow files carries its push sites with it, and `ref_privacy.py`'s `PUSHERS` is keyed on the file. PR 2's move of `tests.yml` into the umbrella must re-key `tests.yml`'s entry in the same diff, and run `python3 -I tools/audit/seat/ref_privacy.py --check` before pushing. Carry: R10-CI-LAYOUT-P2
- `R10-REPLAY-LANE`'s roster `files` names `.github/workflows/nightly.yml`, which this PR creates. Its fixer edits the moved `slow` job there, not in `tests.yml`. Carry: R10-REPLAY-LANE

## Friction

- finding-propagation: unclear: the brief names "the plan addendum A1-A6 / B1-B9 ... find them on the same refs", but neither the design tags nor the roster, the flow-study branch or issue #2495 carries the addendum text. B9 was built from the brief's own sentence ("B9's producer check on the merge_group and recheck events after recheck-gate moves"), and nothing else from the addendum binds PR 1. Carry: R10-CI-LAYOUT-P2
- fixer: cost: CI's job logs live on a blob host this cloud seat's proxy refuses (`gh api .../actions/jobs/<id>/logs` fails with `Forbidden` on the `productionresultssa*.blob.core.windows.net` redirect). So the critical-path case column, and this round's three red logs, were read through the MCP log reader one job at a time. A seat with `gh` logs runs `critpath_fetch.sh` as committed. Carry: R10-CI-LAYOUT-P2
- fixer: cost: governance's `run:` steps write to `$RUNNER_TEMP`, so re-running a skipped step locally from its own text fails (`tee` onto `/sr-self-test.txt`) until `RUNNER_TEMP` is set. A seat replaying a governance job's steps sets it first. Carry: R10-CI-LAYOUT
