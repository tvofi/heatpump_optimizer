R10-CI-LAYOUT PR 1: the nightly lanes leave tests.yml, the pin plan folds into mutation, recheck-gate goes, and W1 removes the C1 composition at its source

Part of #2495 and of #201. Group: R10-CI-LAYOUT-P1 (roster `handoff/audit-r10-roster`), PR 1 of the four-PR CI-layout sequence. PR 0 merged as #2464; PR G (#2529) is open and orders before this one at merge only. The design is phase 1 of `probe/design-ci-rev4` (`1371a0a6`, archived as the tag `archive/probe/design-ci-rev4`), approved at review round 5 (`archive/probe/design-ci-review5`, `afc00bfe`). This PR builds DESIGN-P1 less step 5b, which PR 0 landed. It includes W1 and B9's producer check.

**Owner gate.** This PR is code-owned CI workflows (`/.github/workflows/`, and `/.github/actions/`, which this PR adds to CODEOWNERS) and policy (`dev/governance/rules/ci-autofix.md`, `defect-root-cause.md`, their `rules_sync` outputs, and decision 0011's workflow paragraph). It also raises one row of `tests/ci_budgets.json` (see `## Raise justification`). The CODEOWNER session approves it at its merged head under mandate 6319294694. No required context is added, renamed or removed.

What changes (DESIGN-P1 section 2, read from the ref):

- **(a) `nightly.yml` (`name: Nightly`).** It carries `mutation-nightly`, `mutation-ledger`, `mutation-ledger-push`, `slow`, the schedule and dispatch arm of `nightly-ha`, and `record-autofix`.
  - Its triggers are `schedule: 17 2 * * *` (the one cron, moved), `workflow_dispatch`, and `push: main` (for `record-autofix` alone).
  - Floor `contents: read`; concurrency by run id, never cancelled.
  - Each moved job is verbatim except its `if:` (the recheck clause and `needs: [recheck-gate]` go). That includes `record-autofix`'s automerge step, so its train-hold arm is kept (Lean study K6, carried to this group).
  - `tests.yml` drops `schedule:` and the schedule arm of `coverage`.
  - `nightly-ha` keeps only its pull-request arm in `tests.yml`. Both arms run the composite action `.github/actions/nightly-ha`, so each keeps its `nightly-ha (<image>)` check name.
  - `tests/nightly_status.py` reads `nightly.yml`, and so does its red report's dispatch call. `REQUIRED_LANES` is unchanged.
  - D-1: the record beat's red no longer reddens the Tests push run. The tick still flags it: see the D-1 test below.
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
  - `merge_main_bot.py` `PIN_CHAIN` (three jobs), `merge_train.py` (its beat self-test reads `nightly.yml`), `policy_lint.mjs` `REPORTER_INPUTS` (gains `nightly.yml`), and the `ci-watch.sh` fixtures.
  - `CODEOWNERS` gains `/.github/actions/`; `tests/README.md` and `HANDOVER.md` are updated.
  - `r10_replay_loopnorm.py` reads `slow` from both workflow files.
- **Carried in:** the four stale "a GITHUB_TOKEN push leaves no pull_request run" comments in `tests.yml` (#2394's Friction) now state the measured fact: a bot head's runs are created, held `action_required`, and approved by hpo-runs.

**Deviation from the design, with its evidence.** DESIGN-P1 2(a) deletes `coverage`'s step "Check the restored coverage is main's push run's". Its premise is that the step "executed on the schedule run only" (section 0, item 5). At this base the premise is false.

- The step gates per-script coverage reuse (`W5P_REUSE`) on every pull request with a cache hit, and `entities.py`'s `_cov_steps` pins it.
- Over the 90 PR runs in the critical-path fetch below whose four lanes concluded, the step executed 53 times and was skipped 31 times. The count reads the saved `tests_jobs_<run>.json`'s `coverage` steps by name.

So it is kept. Deleting it would let an unverified cache entry stand in for the base's measurement. The step is not on the static map's drop list, and the static check below passes with it kept.

## Head

`1b4fae9df4762f0d70949c7e5d9f2db78ff92c28`. Its parent `eb804069e` is the code commit `abf4f40b7` merged with origin/main `f2fb1b0e950ecd047b7f08b3adef93776a622540`, an automatic merge with no conflict. `1b4fae9df` adds one file, `dev/audit/harnesses/r10_ci_layout_p1/c1_consumers.sh`, the census wrapper `## Figures` runs. `git merge-base HEAD origin/main` is `f2fb1b0e9`. The suite figures (`entities.py`, the mutants, the self-tests, `structure.py`, `harness_headers.py`) were taken at `eb804069e`, whose tree differs from this head's by that one file. Every local figure was taken on a Linux cloud seat, under `/opt/hpo/venv-ci` (CPython 3.14.7), unless it says otherwise.

## Mutation proof

Six production elements were reverted to their base form at once, in a throwaway detached worktree at this head. Each mutant touches a different artifact, so each failing check names its own mutant. The full run read `6 of 2387 ENTITY CHECKS FAILED`, exactly these:

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

- The unmutated head: `ALL 2387 ENTITY CHECKS PASSED` (`PYTHONPATH=tests/hastub python tests/entities.py`). Before the merge of origin/main the code commit read `ALL 2381`, against `ALL 2375` at the base `49c222280`. The base-to-head difference in count is main's six new checks plus this PR's.
- The **static** half of the design's null control (DESIGN-P1 section 4, `measure/rev/unitcheck2.py static`) uses a closed map, committed as `dev/audit/harnesses/r10_ci_layout_p1/unitcheck_map.json`.
  - Head: `STATIC rows 225->232 lost 0 gained 0 changed 29 (mapped 29) misplaced 0 rc 0`.
  - Planted: deleting one step from `nightly.yml`'s `record-autofix` (a verbatim move must keep it) gives `lost 1 ... rc 1`.
  - Each admitted `changed` row is printed before and after by the same run.
  - `record-autofix` and `mutation-ledger-push` show no row at all: they moved verbatim.
- The **runtime** half (DESIGN-P1 section 4's table) needs this PR's own CI runs and post-merge runs, so it is the orchestrator's. Its pairs are unchanged from the design. The `nightly` and `pin chain` rows are checked after the merge (risks R-2, R-4).
- The critical-path harness's self-test `edge+tail gain 330 s (want 330) ok; null control 0 s (want 0) ok`. The null control is a run whose `closures` already ends before `coverage`.

## Figures

- `python3 -I dev/audit/harnesses/r10_ci_layout_p1/critpath.py RAW CASES --case SCOPED --n 20`: `SCOPED: runs 20; wall median 34.9 min; W1 gain median 8.8 min, min 0.0, max 14.4; runs gaining > 0: 19`.
  - The method is the design's phase-2 critical-path counterfactual (the `critpath` measure on the archived design tag). Every job's duration is held fixed; `closures` starts its measured queue after `closure-scope` instead of after `coverage`; `composed-proof` adds no tail.
  - The input is the 20 newest completed `pull_request` runs of `tests.yml` whose `closure-scope` log reads `CASE: SCOPED`, out of the 37 newest whose four lanes concluded, read 2026-10-21 by `dev/audit/harnesses/r10_ci_layout_p1/critpath_fetch.sh`.
  - On this seat the logs came through the MCP log reader, because the proxy refuses the log blob host.
- The same with `--case FULL`: `FULL: runs 13; wall median 63.8 min; W1 gain median 18.1 min, min 0.0, max 35.6; runs gaining > 0: 11`. All 13 FULL cases name a gate file: `tests/closures.json` 7, `tests/closure.py` 4, `tests/requirements-ci.txt` 1, `.github/workflows/tests.yml` 1.
- **The flow study's claim, corrected.** The model says W1 removes "about 7 min on a FULL-scope train and 19-21 min on a scoped run". Measured on these runs, the ordering is the reverse: a scoped run's median gain is 8.8 min and a FULL run's is 18.1 min. On a FULL run `closures` re-records everything and waited for `coverage`'s whole traced suite; on a scoped run it re-records little and `fast` more often ends the run. Both figures are the design's model over measured job times, not a measured post-W1 run. The post-merge runs are the check.
- `sh dev/audit/harnesses/r10_ci_layout_p1/unitcheck.sh`: `head: ... rc 0`, `plant: ... rc 1 (1 LOST row(s))` (Null control above).
- `sh dev/audit/harnesses/r10_ci_layout_p1/c1_consumers.sh HEAD` (the design's own C1 census, read from `archive/probe/design-ci-rev4`). It lists 6 files, none under `.github/`, `tools/coverage/` or `tests/` except `tests/entities.py`, whose hits are the no-C1-token pin's own pattern. The disposition of each file:
  - `merge_train.py` and `orchestrator_tick.py`: the design's kept fixtures.
  - `dev/audit/harnesses/r10_carry_sweep_rows.py`: a round record naming the old job.
  - `dev/audit/harnesses/r10_ci_layout_p1/critpath.py` and `unitcheck_map.json`: this PR's measurement, which must name the deleted job to model it.
  - `tests/entities.py`: the pin.
  - At `origin/main` the same command lists 12 files.
- `PYTHONPATH=tests/hastub python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: FULL`, reason `.github/actions/nightly-ha/action.yml changes the gate itself`. A gate file, as the design says. The CI `closures` FULL arm and `closures-autofix` own the re-recording.
- `python3 tests/closure.py prune` (before the commit): `pruned 3 phantom entry(ies)`: the deleted allow-list and proof driver in `tests/entities.py`'s closure (2) and its inert reads (1).
- Every-script-once count at this head: `closure.test_scripts()` less `SLOW_GATED` is 34, and coverage_tree.sh's `fast` stage, run by bash, is 20, so 54. This is `_cir_once_count()` in `tests/entities.py`, pinned equal to the budget row.
- `PYTHONPATH=tests/hastub python tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff f2fb1b0e950ecd047b7f08b3adef93776a622540 HEAD`: `Architecture score: dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python tests/closure.py selftest`: `ALL 112 closure shrink pins PASSED`. At the old base `49c222280` it read `ALL 124`; the 12 removed pins were C1's.
- Self-tests:
  - `python3 tools/pr/merge_main_bot.py --self-test`: `40 checks, 0 failed`.
  - `python3 tools/audit/seat/orchestrator_tick.py --self-test`: `172 checks, 0 failed`, against `168` at the base; the four new checks are `MAIN D-1`.
  - `python3 tools/audit/seat/merge_train.py --self-test`: `198 checks, 0 failed`.
  - `python3 tools/audit/seat/record_row.py --self-test`: `all checks passed`.
  - `bash tools/audit/seat/ci-watch.sh --self-test`: `8 checks, 0 failed`.
  - `python3 -I tests/ci_ratchet.py --self-test`: `15 checks, 0 failed`.
- `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`. `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`: `RESULT uncovered_files=0 count`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused, 0 stale allow entries`.
- Carry 3 (#2529's review): `python3 -I tools/audit/seat/selftest_wiring.py --check` after this branch's merge of origin/main reads `selftest_wiring: 38 self-testing, 38 wired, 0 unwired`, rc 0. PR G has not merged, so main's rule is still the narrow one. The check is owed again at the merge that brings PR G in.
- Carry 1 (#2394's Friction): `grep -n -E "GITHUB_TOKEN push (triggers no|leaves no|creates no) pull_request run" .github/workflows/tests.yml .github/workflows/nightly.yml` prints nothing.
- `env PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>`, at this head under `/opt/hpo/venv-ci`: `PRE-PR: 1b4fae9df4762f0d70949c7e5d9f2db78ff92c28 0000000000000000000000000000`, rc 0, `MODE: FULL`, `closures` skipped under the env var (CI's `closures` and `closures-autofix` own it); its figures step is the figure linter over this body.
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

Payments tried:

- Keeping C1 to stay at 53 is the owner's ruling D-4's refused alternative (V2 in DESIGN-P1 2(c)). It keeps two files, a job, a workflow edge and four `closure.py` entry points, so it is no architectural payment.
- Skipping the bare recording would remove the only recording of that script, so it is no payment either.
- No other script could stop running twice: each instrument measures each script once.

Architecture score: dS +0.0000 NULL

## Red checks

- `nightly-status` will be red on this PR. It grades main's last scheduled Tests run, 39563978649 (2026-10-21), where `slow` (job 119101702593) and `mutation-nightly` (job 119101702662) failed. This diff touches `tests.yml`, a reporter input, so it owes an answer.
  - The failing lanes move to `nightly.yml` verbatim, apart from their `if:`. This PR changes no step those jobs run, which the static half shows: `slow|` and `mutation-nightly|` change only in their job rows.
  - The cause is main's, not this diff's.
  - Cheaper detector: none for this PR.
  - After the merge, R-4 applies: dispatch `gh workflow run nightly.yml --ref main` at once, and expect RUNNING, then the lanes' own verdict.
- `closures` will print `UNDER-SCOPED`: this is a FULL run, and `tests/entities.py`'s closure gains `nightly.yml` and the action. `closures-autofix` pushes `ci: re-record closures` from the Linux recording. No seat ran `derive_closures.sh` here (`PREPR_SKIP_CLOSURES=1`).
- `budget-raise-gate` is red until the raise is approved at its head: the CODEOWNER session under the mandate, with `## Raise justification` above.

## Forward-carry

- After this merge, dispatch `gh workflow run nightly.yml --ref main` right away. `nightly-status` on PRs based before the merge reads ABSENT once `tests.yml`'s last schedule run ages past two nights, and on PRs based after it reads RUNNING until that dispatch concludes (DESIGN-P1 risk R-4). The ledger and record-writer environments' first run under `nightly.yml` is also post-merge (R-3). Carry: R10-CI-LAYOUT-P2
- The runtime half of the null control's pin-chain and nightly rows, and W1's critical-path gain, are measured on post-merge runs only. Pin chain: the next PR whose `mutation` refuses must show `mutation-pins` expanding from `needs.mutation.outputs.shards`. W1 gain: `critpath.py`'s model figures are 8.8 min median on scoped runs and 18.1 min on FULL runs. PR 2's unit runs must re-take both before the umbrella builds on them. Carry: R10-CI-LAYOUT-P2
- `coverage`'s step "Check the restored coverage is main's push run's" stays, against DESIGN-P1 2(a)'s deletion, because it executed on 53 of the 84 sampled PR runs that had the step (see the body's deviation note). PR 2's unit that moves `coverage` must keep it. Carry: R10-CI-LAYOUT-P2
- `fast`'s two warm-cache steps keep a `github.event_name == 'schedule'` arm, which is dead now that `tests.yml` has no schedule (`fast` never ran on one anyway). This PR leaves those steps untouched, because they are outside the design's map. The umbrella's split of `fast` should drop the arm. Carry: R10-CI-LAYOUT-P2

## Friction

- finding-propagation: unclear: the brief names "the plan addendum A1-A6 / B1-B9 ... find them on the same refs", but neither the design tags nor the roster, the flow-study branch or issue #2495 carries the addendum text. B9 was built from the brief's own sentence ("B9's producer check on the merge_group and recheck events after recheck-gate moves"), and nothing else from the addendum binds PR 1. Carry: R10-CI-LAYOUT-P2
- fixer: cost: CI's job logs live on a blob host this cloud seat's proxy refuses (`CONNECT tunnel failed, response 403`), so the critical-path case column was read through the MCP log reader one job at a time. A seat with `gh` logs runs `critpath_fetch.sh` as committed. Carry: R10-CI-LAYOUT-P2
