# Consolidating `.github/workflows/tests.yml`: a design (PR 1)

Read-only design seat. Tree: `origin/main` at `07a09406a1cc97076a6f28581f87f313b322a6b6`.
Measured 2026-10-18. Nothing in the repository was changed.

**Revision 1** (design-revision seat, 2026-10-18) answers the design review
`probe/design-ci-review` (`f7b28312`, verdict *revise*). This file is now **PR 1** of
the two-PR plan: phase 1, with section 2(c) replaced by phase 2's W1 (drop the C1
composition, at its source; owner ruling D-4), plus the inert `ci.yml` stub. What
changed and why is in `RESPONSE.md`, one section per review item; inline markers
read *(rev1, item N)*. Paths: this design's measurements are under `measure/p1/`
(cited below by bare file name, as before), phase 2's under `measure/p2/`, and
revision 1's own instruments under `measure/rev/`. Owner rulings already made: D-1
approve; D-4 drop C1 in PR 1 once the proof is shown covered (section 2(c) shows it).

Every figure below is printed by a script under `measure/`, run over the saved API
responses in `measure/raw/` (fetched by `measure/fetch.sh`, read-only GETs of
`actions/workflows/tests.yml/runs` and `actions/runs/<id>/jobs?filter=latest`):

| enumerator | prints |
|---|---|
| `python3 -I measure/p1/measure.py measure/p1` | `summary.md`, `jobs.tsv`: per-job executed/skipped counts, median/p90/max seconds over the 20 newest completed `pull_request` runs, 5 `push` (main) runs and 5 `schedule` runs |
| `python3 -I measure/p1/tail.py measure/p1` | `tail.txt`: which job ends each PR run, how far past the last required Tests job, and queue latency per job |
| `python3 -I measure/p1/noop_tail.py measure/p1` | `noop_tail.txt`: seconds each PR run would end sooner without composed-proof's `none` arm |
| `python3 -I measure/p1/dispatch.py measure/p1` | `dispatch.txt`: recheck-gate's cost on the 10 newest `workflow_dispatch` runs |
| `python3 -I measure/p1/stepset.py measure/p1/raw --before … --after …` | the migration's runtime null control (section 4) |
| `python3 -I measure/rev/unitcheck2.py static BEFORE.yml AFTER.yml --map MAP.json` | the migration's static null control (section 4; rev1, item 9) |
| `python3 -I measure/rev/c1_counterfactual.py measure/p2/raw --sweep` | `measure/rev/c1_sweep.txt`: W1's PR wall-clock change at each bare cost (rev1, item 8) |
| `sh measure/rev/c1_consumers.sh <rev>` | `measure/rev/c1_consumers.txt`: every C1 reader and writer (rev1, item 8) |

`measure/p1/readers.md` is the full reader survey: one section per job id, each reader as
`path:line` with what it does with the name, the exact `git grep` commands, and
sections (a)–(i) on the agreement pair, loop guards, pr-contract, the tick, the merge
train, closures/INERT, required-check lists, workflow triggers and nightly-status.
Section 1 here condenses it. Where the two disagree, `readers.md` is the record.

## 0. What the measurements change about the brief

1. **Moving skipped jobs saves no runner time and no PR wall clock.** A job skipped
   by its `if:` never takes a runner. Over the 20 PR runs, `mutation-nightly`,
   `mutation-ledger`, `mutation-ledger-push`, `slow`, `recheck-gate` and
   `record-autofix` executed 0 times (`summary.md`). Moving them buys only these:
   - six of the seven rows the design removes from every PR check list (the
     seventh is `mutation-pin-plan`, section 2(b));
   - the deletion of `recheck-gate` and the `recheck` arms of eleven `if:` expressions;
   - a nightly whose failures no longer share a workflow, and so a verdict, with the
     PR gate.
   It is worth doing for those reasons. It is not a speed change.
2. **The one measurable PR wall-clock waste in the small jobs is composed-proof**
   *(rev1: it leaves the PR graph with W1, section 2(c), which also removes the
   `coverage → closures` edge behind it).* It
   is the last job to finish in 17 of 20 PR runs (`tail.txt`). It ran its `none` arm
   in 14 of the 18 runs where it concluded. In those runs the run would have ended a
   median **18.5 s** sooner, and up to 128 s sooner, without it (`noop_tail.txt`):
   it takes a runner only to decide there is nothing to prove.
3. **recheck-gate is off the critical path.** On dispatch runs it takes a median
   7 s. Every lane that needs it except `briefs`, `typing` and `mutation` also
   needs `closure-scope`, which takes a median 19 s in parallel (`dispatch.txt`,
   `summary.md`). Deleting it saves a job, not seconds.
4. **Two of the five measured push runs on main were red only because of
   `record-autofix`** (runs 39156632994 and 39156244284; every other job succeeded
   or skipped). `tools/release/stamp.py` gates on "the Tests workflow for HEAD
   … succeeded" (`TESTS_WORKFLOW = "Tests"`, :13,173). So a delivery-row beat
   failure currently reads as main's code verdict. This is a decision for the
   owner; see D-1.
5. **The nightly re-measures a tree a push already measured.** The schedule run's
   `coverage` and `closures` execute a subset of the push run's steps. Running
   `stepset.py --before 39106988523 --after 39158143952` shows the schedule side
   alone carries only three steps:
   - `closures | Write the recordings' tree hash`
   - `closures | Upload closure recordings` (the tree-named upload)
   - `coverage | Check the restored coverage is main's push run's`

   Those three exist for `composed-proof`'s nightly arm and nothing else, apart from
   `closures`' push-side `proof-consume`, which looks the artifact up by tree name
   and fails closed to a fresh re-record.

## 1. Inventory

Columns:
- **runs when**: the job-level `if:`, condensed. `recheck` means `workflow_dispatch`
  with `needs.recheck-gate.outputs.recheck == 'true'`.
- **PR exec**: executed out of 20 PR runs, then median/p90 seconds over executed
  success-or-failure jobs (`summary.md`).
- **req**: in ruleset 23698884's required set, as recorded in
  `tools/policy/fixtures/required-contexts.json`.

No job has a `name:` key, so each check name is the job id, plus ` (<matrix>)` for a
matrix job.

| job | runs when | needs | outputs/artifacts and their consumers | matrix | PR exec, s | req | readers outside tests.yml (full list: `readers.md`) |
|---|---|---|---|---|---|---|---|
| `cancel-superseded` | PR, sender not `github-actions[bot]`, same repo; `actions: write` | – | – | – | 7/20, 8/10 | no | `tests/entities.py:24852` `_NS_OVERRIDES` (exact override set), `:28350` `_PRW_SUBJECTS`; **same id in `codeql.yml:100`** (two check runs share the name) |
| `recheck-gate` | `workflow_dispatch` only | – | `recheck` → fast, browser, briefs, typing, coverage, coverage-ratchet, mutation, mutation-nightly, mutation-ledger, slow | – | 0/20 (dispatch: 7 s, n=10) | no | `entities.py:32477` (evaluates the ledger `if:` with `needs.recheck-gate.outputs.recheck`); `dev/governance/rules/ci-autofix.md:81` (policy); `tools/audit/seat/ci-watch.sh:112,128` fixtures; the **input** `recheck` is keyed by `merge_train.py:290` (`-f recheck=true`) and `release.yml:71` (comment) |
| `fast` | push, PR, merge_group, recheck; stands down at **step** level (`fast_skip`) | recheck-gate, closure-scope | `ci-metrics-fast` → ci-ratchet; result → claims-autofix, lane-proofs | `python-version: [3.14]` | 20/20, 1241/2661 | `fast (3.14)` | required-contexts.json; `entities.py:1665-1686` (matrix vs README), `:27629` (not in GOV); `tests/ci_ratchet.py` LANES; `stamp.py:13`; `ci_predict.py` |
| `browser` | as fast, plus `browser_skip != 'skip'` (job level) | recheck-gate, closure-scope | result → lane-proofs | – | 20/20, 241/248 | yes | required-contexts.json; `entities.py:27629` |
| `briefs` | push, PR, merge_group, recheck | recheck-gate | – | – | 20/20, 27.5/29 | yes | required-contexts.json; `governance_cost.py:61-64` GOV and `agreement_py.py:106` `pin={"briefs"}` (the governance-workflow-jobs pair); `entities.py:27629` |
| `typing` | push, PR, merge_group, recheck | recheck-gate | `typing` artifact | – | 20/20, 79/91 | yes | required-contexts.json |
| `coverage` | push, PR, **schedule**, recheck; `coverage_skip` | recheck-gate, closure-scope | `coverage-json` → coverage-ratchet, graders-head-copy; `composed-closures` → closures, composed-proof; `ci-metrics-coverage` → ci-ratchet; per-script cache on push | – | 20/20, 970/1244 | no | `ci_ratchet.py` LANES; `entities.py` (via closures/proof checks) |
| `coverage-ratchet` | push, PR, recheck; `coverage` not skipped; **pinned grader** | recheck-gate, coverage | – | – | 20/20, 9.5/11 | no | `entities.py:30627-30643`, `:26687` (graders-head-copy literal); decision 0013:196,226 |
| `mutation` | push, PR, merge_group, recheck | recheck-gate | `mutation-table` → pin-plan, pins; result → pin-plan, pins, autofix | – | 20/20, 35.5/836 | yes | required-contexts.json; `merge_main_bot.py:146` PIN_CHAIN; `entities.py:30623,32162,32185`; `cfr_exclusions.json:13`; `ci_predict.py`; `ci_predict_replay.sh:36` |
| `mutation-pin-plan` | PR, same repo, `mutation` failed | mutation | `shards`, `count` → mutation-pins | – | 2/20, 16/17 | no | `entities.py:34726-34735`; PIN_CHAIN (+ self-test asserting the four-name set) |
| `mutation-pins` | as pin-plan | mutation, pin-plan | `mutation-pins-<n>` → mutation-autofix | `shard: fromJSON(...)`, ≤12 | 2/20, 2940/3899 | no | PIN_CHAIN (suffix-aware); `entities.py:32163-32197,34249-34260` |
| `mutation-nightly` | schedule; dispatch not recheck | recheck-gate | `mutation-table-full`; restores `pool-seconds-*` | – | 0/20; sched 6485/14152 | no | `nightly_status.py:158` REQUIRED_LANES; `entities.py:24880-24894` (schedule-only derivation), `:30624,32502,34114,34968`, `:30760` (HANDOVER text) |
| `mutation-ledger` | main; schedule; dispatch not recheck | recheck-gate | `mutation-ledger` → ledger-push; saves `pool-seconds-<run_id>` | – | 0/20; sched 12585/14495 | no | REQUIRED_LANES; `entities.py:32424-32495` (`if:` reach matrix) |
| `mutation-ledger-push` | main; schedule or dispatch; ledger succeeded; `environment: ledger` | mutation-ledger | pushes `ci: record nightly kills` | – | 0/20; sched 19/31 | no | REQUIRED_LANES; `entities.py:32425,32604` (`_LEDGER_JOBS`), `:34123`; `mutation_table.py:1359` DRAIN_SUBJECT |
| `slow` | schedule; dispatch not recheck | recheck-gate | – | – | 0/20; sched 561/735 | no | REQUIRED_LANES; `entities.py:32502,35513-35516` |
| `nightly-ha` | schedule, dispatch, PR when `closure-scope` says `nightly_ha` | closure-scope | – | `image: [2025.2.0, stable]` | 2/20, 145/174; sched 145/171 | no | REQUIRED_LANES (suffix stripped, `:310`); `entities.py:20239-20265,32503,32517-32536` |
| `nightly-status` | PR; read-only `actions: read`; **pinned grader** | – | – | – | 20/20, 10/12 | no (deliberately) | `policy_lint.mjs:6096` MAIN_STATE_REPORTERS (REPORTER_INPUTS includes tests.yml); `merge_train.py:3097` default `--ignore-red`; `nudge.md:23,52`; `entities.py:24812-24864`; tick NIGHTLY_CLASS |
| `graders-head-copy` | PR | coverage | – | – | 20/20, 18/97 | no | `entities.py:26775-26849` (job equals a canonical literal) |
| `lane-proofs` | PR; dispatch with `inputs.recheck == 'true'`, `no-skip != 'true'` | closure-scope, fast, coverage, browser | `lane-proof-*` caches → next run's closure-scope | – | 20/20, 6/8 | no | **none** |
| `closure-scope` | PR, merge_group, dispatch | – | 12 outputs → fast, browser, coverage, nightly-ha, closures, lane-proofs | – | 20/20, 19/21 | yes | required-contexts.json; `PR_ONLY` in `merge_train.py:286`, `orchestrator_tick.py:120`; `entities.py:20039-20064,32530`; **`a1_dispatch_arms.sh:67,135` hard-codes `steps[2]`** |
| `closures` | `!cancelled()` (every event); `actions: read` | closure-scope, coverage | `closure-recordings` → closures-autofix; `closure-recordings-tree-<T>` (dispatch, schedule) → push proof-consume, composed-proof; `ci-metrics-closures` → ci-ratchet | – | 20/20, 1088/1576 | yes | required-contexts.json; `ci_ratchet.py` LANES; `autofix_statuses.sh:56`; `ci_predict.py`; `stamp.py:13`; `entities.py:20018,20067,24853,27629,29595` |
| `composed-proof` | schedule, PR | coverage, closures | – | – | 20/20, 16/1220 | no | fixtures only (`merge_train.py:2494,2952`, `orchestrator_tick.py:2534`); `composed_proof.sh` message prefix |
| `ci-ratchet` | push to main; `actions: read` | fast, coverage, closures | – | – | 0/20; push 56/62 | no | `entities.py:32938,24852`; `ci_ratchet.py` (workflow name `Tests`) |
| `closures-autofix` | PR, same repo, `closures` failed; `contents/actions: write` | closures | pushes `ci: re-record closures`, dispatches Tests/Hassfest/Validate/CodeQL | – | 2/20 (both cancelled) | no | `closure.py:2240-2304` AUTOFIX_QUIET/_REMEDY (`--job`); `entities.py:19609-20215,27399,28352`; `autofix_statuses.sh:41,55`; tick regexes; `ci-autofix.md` table |
| `claims-autofix` | PR, same repo, `fast` failed; write | fast | pushes `ci: drop inherited claims` | – | 3/20, 15.5/17 | no | as closures-autofix; `entities.py:27407` (`mayAdd`) |
| `mutation-autofix` | PR, same repo, `mutation` failed; write | mutation, mutation-pins | pushes `ci: pin killed mutants` | – | 2/20, 28/36 | no | PIN_CHAIN; as closures-autofix; `entities.py:32137-32197` |
| `record-autofix` | main; push, schedule, dispatch | – | pushes `ci: record delivery rows`, opens/merges the record PR | – | 0/20; push 119/162, sched 84/95 | no | `entities.py:26403-26541`; `merge_train.py:2971-2975` (self-test reads tests.yml text); tick NIGHTLY_CLASS/BOT_LANE; `delivery-status-tracking.md:33` |

Cross-cutting readers, any of which a job edit can break:
- `tests/entities.py:1636` `_workflow_job` does `text.index("\n  {name}:\n")`. A
  removed or renamed job it reads by literal name raises ValueError at module
  level, which kills the whole script, not one check.
- `entities.py:24796,24882,32599` loop over every job id.
- `entities.py:32496-32503` asserts one cron, `17 2 * * *`.
- `entities.py:27701-27752,28003-28036`: every required context has a producer,
  none is skippable on `pull_request: edited`, and every producer runs on
  `merge_group`.
- `tests/closure.py:476`: tests.yml is in `GATE_FILES`, not INERT and not a
  closure. It is recorded inside the closures of `tests/entities.py` and
  `tests/harness_headers.py`.
- `pr-contract-rerun.yml:30-32`, `stamp.py:173` and `ci_ratchet.py:185` key on
  the workflow **name** `Tests`. `entities.py:28511-28575` derives the rerun list
  from every workflow listing `pull_request`.
- `orchestrator_tick.py` and `merge_train.py` read the required set live from the
  ruleset, minus `PR_ONLY`.
- The agreement pair (`agreement_py.py:89-112`) compares GOV against the job ids of
  every workflow file. The only tests.yml id in either set is `briefs`.

## 2. Target layout

The result: **tests.yml goes from 27 job ids to 19**, and a new **`nightly.yml`
(`name: Nightly`) carries 6**. `composed-proof` leaves both: with the C1 composition
removed at its source (2(c)) it has nothing to prove. PR check rows fall by 8. No
required context changes. *(rev1, item 8: phase 1 moved `composed-proof` into
`nightly.yml` as a self arm and added it to `REQUIRED_LANES`; with W1 neither
happens.)*

### (a) Scheduled-only jobs leave the PR graph: `nightly.yml`

`nightly.yml`:
- **Triggers:** `schedule: "17 2 * * *"` (the one cron, moved), `workflow_dispatch`,
  and `push: branches: [main]`. The push trigger exists only for `record-autofix`;
  see D-1.
- **Floor:** `permissions: contents: read`. **Concurrency:** group by run id, never
  cancelled (as tests.yml does for non-PR events).

| job | moves from | `if:` in nightly.yml | change |
|---|---|---|---|
| `mutation-nightly` | tests.yml, verbatim | `github.event_name != 'push'` | `needs: [recheck-gate]` dropped |
| `mutation-ledger` | verbatim | `github.ref == 'refs/heads/main' && github.event_name != 'push'` | as above |
| `mutation-ledger-push` | verbatim, `environment: ledger` | unchanged, less the recheck clause | none (the `ledger` environment's branch rule is per ref, not per workflow) |
| `slow` | verbatim | `github.event_name != 'push'` | `needs: [recheck-gate]` dropped |
| `nightly-ha` | the schedule/dispatch arm | `github.event_name != 'push'` | steps move to a composite action `.github/actions/nightly-ha/action.yml`, shared with tests.yml's PR arm. Check names stay `nightly-ha (2025.2.0)` / `nightly-ha (stable)`. A reusable workflow would rename them `nightly-ha / <job> (…)`, which `nightly_status.missing_lanes` would read as MISSING |
| `record-autofix` | verbatim | main; push, schedule, dispatch | none (see D-1) |

tests.yml then drops `schedule:` from `on:`.
- `coverage` loses `schedule` from its `if:`.
- `closures` keeps `!cancelled()`, which on tests.yml's remaining events is push,
  PR, merge_group and dispatch.
- `closures`' tree-hash write and the tree-named upload keep only their
  `workflow_dispatch` arm, which serves the batch proof's consume (the push run's
  `proof-consume` looks the artifact up by tree name and fails closed to a fresh
  re-record).
- `coverage`'s step "Check the restored coverage is main's push run's" is deleted.
  It executed on the schedule run only (section 0, item 5), for `composed-proof`'s
  nightly arm, which no longer exists. *(rev1, item 8)*
- `nightly-ha` stays in tests.yml for the PR arm alone:
  `github.event_name == 'pull_request' && needs.closure-scope.outputs.nightly_ha == 'true'`.

Saving: 5 job rows (`mutation-nightly`, `mutation-ledger`,
`mutation-ledger-push`, `slow`, `record-autofix`) on every PR run, push run and
dispatch run. Runner time per night falls by the schedule run's `coverage` and
`closures`: a median 827 s + 1676 s (`summary.md`, schedule), and by the nightly
`composed-proof` arm. The night's wall clock does not move: `mutation-ledger`, at a
median 12585 s, is its critical path either way. PR wall clock: 0 s from (a); W1 in
2(c) is the PR wall-clock change.

**Considered: a one-job `record.yml`** (the review's optional note), which would
spare `nightly.yml` its `push` trigger and five skipped rows on each push to main.
Not taken: it adds a file, a second cron and a third `entities.py` reader set
(`_RAF_JOB_RAW`, the one-cron check) for rows only main's push runs show, and
`nightly_status.py` already ignores a `push` run of the workflow it reads
(`VERIFYING_EVENTS` is `schedule` and `workflow_dispatch`, :177).

What could break:
- **`tests/nightly_status.py`** must point `DEFAULT_WORKFLOW` at `nightly.yml`
  and change the red report's `gh workflow run tests.yml --ref main` (:209) to
  `nightly.yml`. `REQUIRED_LANES` is unchanged: `composed-proof` is not added
  *(rev1, item 8)*.
  - It is a pinned grader: every PR runs its **base's** copy. So PRs based before
    the merge keep reading tests.yml. Tests.yml's first post-merge cron produces no
    scheduled run, because tests.yml no longer has a schedule. Their newest
    concluded tests.yml schedule run then ages past `MAX_AGE_NIGHTS = 2` and they
    read ABSENT (red).
  - It is not required, and pr-contract exempts it by name (MAIN_STATE_REPORTERS),
    so this blocks nothing. It clears when the merge-main bot brings main in.
  - The first PRs based after the merge read `nightly.yml`, which has no run until
    one is dispatched. **Dispatch `gh workflow run nightly.yml --ref main` right
    after the merge.** A dispatch on main is a verifying event (`VERIFYING_EVENTS`).
    Expect RUNNING (red) for the ~3.8 h it takes.
- **Every `entities.py` reader of a moved job** (inventory rows above) moves from
  `_TESTS_YML` to a new `_NIGHTLY_YML`. That covers:
  - the `_NS_SCHEDULE_ONLY` derivation, now over nightly.yml less `record-autofix`;
  - the `if:` reach matrix (drop the `needs.recheck-gate.outputs.recheck` context
    key);
  - the one-cron check, now in nightly.yml;
  - `_LEDGER_JOBS`, `_RAF_JOB_RAW` and `_NHA_JOB`, which now reads the composite
    action;
  - the override set: nightly.yml has none, asserted as such;
  - the composed-proof pins (`entities.py:33134-33184`), deleted with W1 (2(c)).

  A missed one is a module-level ValueError: loud, and caught by `fast` on the PR.
- **`merge_train.py:2971-2975`**: its self-test reads tests.yml for
  record-autofix's guard strings. Point it at nightly.yml.
- **`policy_lint.mjs` REPORTER_INPUTS** (:6097-6102): add `nightly.yml`, or
  nightly-status's red is exempted on a PR that changes what it reads.
- **`tests/closure.py` GATE_FILES**: add `.github/workflows/nightly.yml`,
  `.github/actions/nightly-ha/action.yml` and the `ci.yml` stub (section 4). By the
  comment's own criterion at :462-475, the first two run gate scripts (`SLOW`,
  `tests/rolling.py`, `mutation_table.py`); the stub becomes the umbrella that
  decides `GATE_SCOPE` in PR 2. This also satisfies the rule that a new tracked file
  is deliberately classified. Remove `tools/coverage/composed_proof.sh` (:556) with
  W1.
- **CODEOWNERS**: `/.github/workflows/` is already `@tvofi`. Add
  `/.github/actions/ @tvofi`. `codeowners_gap.py --check` refuses an executed file
  with no owner.
- **Policy text** (owner approval before merge, CLAUDE.md):
  - `dev/governance/rules/ci-autofix.md:81-82` ("`recheck-gate` treats `ci:` as
    PR-like (not `slow`)");
  - `dev/governance/rules/defect-root-cause.md:143` (names `tests.yml` among
    what `nightly-status` reads; it becomes `nightly.yml`) and `:146` ("dispatch
    Tests on the default branch" becomes Nightly) *(rev1, item 11: phase 1 named
    only :146)*;
  - then `node tools/policy/rules_sync.mjs` regenerates `.claude/rules` and
    `.cursor/rules`.

  Also update `dev/programme/HANDOVER.md:310-314` and `tests/README.md:444`.
- **Harnesses that read the moved lanes by workflow** *(rev1, item 11)*:
  `dev/audit/harnesses/r10_replay_loopnorm.py:64-73` lists `tests.yml` runs and
  selects the `slow` job. After the merge the lane's runs are `nightly.yml`'s; the
  harness reads both files, older runs from `tests.yml` and newer from
  `nightly.yml`, so its series stays continuous. `ci_script_seconds.py`,
  `merge_throughput.py` and `superseded_runs.py` read Tests push or PR runs, which
  PR 1 leaves in `tests.yml`; PR 2 changes them (DESIGN-P2.md section 9).
- **Lost signal.** On a day with no merge, nothing re-runs `coverage` and
  `closures` at main's tip. Today the nightly does, so a runner-image change that
  shifts a closure surfaces overnight; after this it surfaces on the next push to
  main. It is still within one merge, which is the gate's stated safety argument
  (CLAUDE.md rule 1). If the owner wants the canary, `nightly.yml` can run
  `gh workflow run tests.yml --ref main`. That costs a FULL fast+coverage+closures,
  about 50 min of runners, and is more than today's nightly checks (today's
  schedule run skips `fast`).

### (b) The mutation autofix chain

Today the PR side is `mutation → mutation-pin-plan → mutation-pins (N) →
mutation-autofix`, and the nightly side is `mutation-ledger → mutation-ledger-push`.

| boundary | what keeps it | consequence |
|---|---|---|
| `mutation` is required and runs PR code with no write grant | the ruleset | stays a job |
| a driver never runs beside a write-capable token (D11-s1-03) | separate jobs | `mutation-pins` (drivers, read-only) and `mutation-autofix` (`contents/actions: write`, no driver) stay apart |
| the matrix width must be a job output | `fromJSON(needs.X.outputs.shards)` | something upstream of `mutation-pins` must output it |
| the ledger App token (`environment: ledger`) never meets a driver | separate jobs | `mutation-ledger` and `mutation-ledger-push` stay apart |
| loop guard `ci: pin killed mutants` | `autofix_allowed(loop_subject=…)` reads the head subject, not a job | unaffected by job layout |

**Fold `mutation-pin-plan` into `mutation`.**
- Add a final step, `id: plan` and `if: always()`, that runs the same
  `mutation_table.pin_shard_count` over the table `mutation` just wrote. Expose
  `outputs: shards, count` from `mutation`. `mutation-pins` then needs only
  `[mutation]`.
- Pin-plan is read-only, runs the head's `mutation_table.py` exactly as `mutation`
  does, and has no grant. Folding crosses no boundary.
- `mutation`'s own conclusion is unchanged: the step only writes `$GITHUB_OUTPUT`
  and must not fail. Guard it as pin-plan does today with
  `touch "$RUNNER_TEMP/mutation-table.txt"`.

Saving: one job on each PR whose `mutation` refuses (2 of 20). On those it removes
16 s of execution and a measured 3.5 s of queue (`tail.txt`) from the critical path
to `mutation-autofix`. Rows: −1.

Rejected:
- **Merging the three `*-autofix` jobs.** One job would wait for `mutation-pins`
  (2940 s median) before repairing `closures`. It would also put three subjects'
  pushes in one job, and each next run reads one head subject against its own loop
  guard.
- **Folding `mutation-pins` into `mutation`.** That turns the required context's
  conclusion into "measured pins" and holds it ~49 min.

What could break:
- `tools/pr/merge_main_bot.py:146` PIN_CHAIN drops `mutation-pin-plan`, and its
  self-test (:340-363, "the chain set equals these four") becomes three. Pin-plan
  sat between `mutation` and `mutation-pins`, and `mutation` is in the chain, so
  while `mutation` runs the bot still sees the chain in flight. No gap opens.
- `entities.py:34726-34735` reads `_MUT_PLAN` and asserts
  `fromJSON(needs.mutation-pin-plan.outputs.shards)`. It becomes the `mutation`
  job and `needs.mutation.outputs.shards`.
- An output set by a step that ran after a failing step needs `if: always()` on
  that step. Without it, `shards` is empty on exactly the runs that need it, and
  `fromJSON('')` fails `mutation-pins` at expansion. The entities check should
  assert the `always()`.

### (c) The small proof jobs, and W1: drop the C1 composition at its source

*(rev1, item 8; owner ruling D-4.)* Phase 1's original 2(c), re-gating
`composed-proof` at job level, is withdrawn: the job leaves the graph instead.

**What C1 is.** `closures` re-records every in-scope script under `strace`. Round 9's
C1 lets one script, `tests/boost_drift_replay.py` (the only entry of
`tests/composed_closures.json`), be recorded once inside `coverage`'s traced run
(`tools/coverage/coverage_tree.sh:190-200` runs it through `closure.py record`), handed
to `closures` as the `composed-closures` artifact, verified by `closure.py
composed-verify` and consumed in place of a bare recording. `composed-proof` proves
the traced recording equals a bare one. The `needs: coverage` edge exists for that
artifact alone (DESIGN-P2.md section 3: it costs a median 972 s of `closures` idling).

**The change, at the source, in this PR.** Every reader and writer of the composition,
as `sh measure/rev/c1_consumers.sh origin/main` lists them (`c1_consumers.txt`, 10
files):

| file | what goes |
|---|---|
| `tools/coverage/coverage_tree.sh` | the `COMPOSED` list (:147-160, `closure.py composed-list`) and the composed branch (:190-200): `boost_drift_replay.py` runs under coverage like every other script, with no `closure.py record` and no `strace` |
| `.github/workflows/tests.yml` | `coverage`'s `composed-closures` upload (:908-919); `closures`' `needs: coverage`, its fetch / verify / stage steps (:2584-2610) and `COMPOSED_CONSUMED`; the whole `composed-proof` job (:2760-2836); the schedule-only coverage-restore check and nightly-arm upload (2(a)); the header comments (:728-730) |
| `tests/derive_closures.sh` | the `COMPOSED_CONSUMED` case in `rec()` (:142-155): every script records bare |
| `tests/closure.py` | `COMPOSED`, `CHEAP_ARGV_OR_ENV`, `composed_verify`, the `composed-list` and `composed-verify` subcommands and their self-tests (:2529-2700, :4274-4379, :5006-5042); `GATE_FILES`' `composed_proof.sh` (:556) |
| `tests/composed_closures.json`, `tools/coverage/composed_proof.sh` | deleted |
| `tests/entities.py` | the C1 pins (:33134-33184) |
| `tests/closures.json` | **not by hand**: the three entries naming the deleted files (:1424, :1530, :3378) become phantoms, which `closures` refuses and the autofix cannot drop (`ci-autofix.md`, "a committed phantom"); `python3 tests/closure.py prune` repairs them, then the FULL run's `closures-autofix` records the rest on Linux |
| `merge_train.py:2494`, `orchestrator_tick.py:2534` | **kept**: self-test fixtures for "a non-required lane that never concludes", named after `composed-proof`; the name is arbitrary there |

**Is the proof covered? Yes, by construction, once the composition is gone at its
source.** `composed-proof` checked one property: the recording `closures` consumed
from `coverage` equals what a bare recording reads. After this PR nothing produces a
traced recording and nothing consumes one, so `closures` records every in-scope
script bare, through `derive_closures.sh`'s `rec()`: the path every other script
already takes, and the fail-closed path every C1 refusal took ("a refusal consumes
nothing: every script records bare"). There is no second recording left for the
property to compare. The review's condition (item 8) is exactly this: the removal at
the source in the same PR, so `coverage` stops paying `strace` for a recording no one
reads. Phase 2's "can later delete" is withdrawn.

Two checks make it permanent, both in this PR:
- `entities.py` asserts that `tests.yml`, `coverage_tree.sh`, `derive_closures.sh`
  and `closure.py` contain none of the C1 tokens `c1_consumers.sh` greps.
- The PR body carries `sh measure/rev/c1_consumers.sh HEAD` at the PR head: it must
  list only the two fixture files above.

**The cost, at measured bare seconds** (`measure/rev/c1_counterfactual.py`, phase 2's
replay with the bare cost as a parameter; `c1_sweep.txt`). Phase 2 charged the 239.1 s
recorded in `tests/closures.json` and called it an upper bound. It is not: the CI
runner's bare recordings of `boost_drift_replay.py` measured 221 / 430 / 424 / 480 s
(design review `ev/boost_bare_seconds.txt`).

| bare cost charged | V1 (drop C1) median gain | runs slower | worst run | V2 (split, keep C1) median gain |
|---|---|---|---|---|
| 239.1 s (recorded) | 342 s | 1/24 | −163 s | 343 s |
| 427 s (median of the 4 CI recordings) | 264 s | 2/24 | −351 s | 343 s |
| 480 s (slowest CI recording) | 232 s | 2/24 | −404 s | 343 s |

V1's median gain falls to V2's at a bare cost of 148 s and to zero only at 1065 s.
Not modelled, and only in V1's favour: V1 also takes `strace` off `coverage`'s own run
of the script (`coverage`'s end is held at its measured time).

**So V1 is not as fast as V2** (phase 2's "V1 is as fast" is withdrawn): at measured
cost it gives up a median 79-111 s per PR run against V2. It is chosen for what it
deletes. V2 keeps every C1 part above and adds a job and a second artifact hop; V1
removes two files, a job, a workflow edge, four `closure.py` entry points and their
pins, and leaves one recording path. The owner's ruling D-4 stands on these numbers.

What could break:
- `closures` loses `needs: coverage`. `measure/p2/deps.txt` shows the edge carries
  only `composed-closures`; `closures`' other inputs come from `closure-scope`.
- A scoped PR whose diff reaches `boost_drift_replay.py` now records it bare in
  `closures`: 221-480 s more there, inside `closures`' 100-minute timeout.
- On a push to main, `closures` (median 1554 s plus at most 480 s) stays under `fast`
  (median 2893 s); main's wall clock does not move (`summary.md`, push table).

Why each other merge is refused (unchanged from phase 1):
- **coverage-ratchet + ci-ratchet** share `coverage`'s output.
  - coverage-ratchet is a pinned grader whose isolation rule is "nothing before it
    in this job runs the pull request's code".
  - The merged job would carry ci-ratchet's `actions: read` override on PRs.
    `entities.py:24852` pins the override set, and the code comment there asks that
    any widening be argued.
  - It would also wait for `fast`, which is last in most PR runs.
  - The saving is one ~8 s job on push.
- **lane-proofs into the lanes it records.** lane-proofs is a separate job so the
  proof is written by a job that runs no PR code and has no checkout. Folding its
  cache save into `fast`, `coverage` or `browser` would let the PR's code, which
  runs earlier in that job, reach the step that writes the green proof the next
  run skips on.

### (d) The gate and prelude jobs

- **Delete `recheck-gate`.** After (a), no tests.yml lane is nightly-only, so every
  `workflow_dispatch` of tests.yml is PR-like.
  - Every `needs.recheck-gate.outputs.recheck == 'true'` arm becomes
    `github.event_name == 'workflow_dispatch'`. That is the job `if:`s of
    `fast`, `browser`, `briefs`, `typing`, `coverage`, `coverage-ratchet` and
    `mutation`, plus `fast`'s drift-cache step `if:`s.
  - `needs: [recheck-gate, …]` loses the entry.
  - The `ci:`-subject sniff disappears with it. Autofix dispatches pass no inputs
    and now get the PR-like set by event alone, which is what the sniff existed to
    produce.
  - **Keep the `recheck` and `no-skip` inputs declared.** `merge_train.py:290`
    passes `-f recheck=true`, and a dispatch with an undeclared input is refused by
    the API. `lane-proofs` and `closure-scope`'s laneskip step key on
    `inputs.recheck`, and they keep exactly today's meaning.
  - Saving: one job per dispatch run (10 of 10 sampled were recheck-arm dispatches),
    0 s critical path (`dispatch.txt`).
- **Do not fold `cancel-superseded` and `nightly-status`.**
  - Their grants differ: `actions: write` against a block that `entities.py:24864`
    pins to carry no `write` at all.
  - Their events differ: cancel-superseded skips bot-sent and fork runs, while
    nightly-status runs on both.
  - Neither is on the critical path: 8 s and 10 s, in parallel with
    closure-scope's 19 s.
- **Do not fold `nightly-status` into `closure-scope`.** It would make a main-state
  reporter's red a required context's red. It is deliberately not required.

What could break:
- A human who dispatches `tests.yml` on main expecting the nightly lanes gets the
  PR-like set instead. The fix is the updated `nightly_status.py` message and
  `defect-root-cause.md:146`.
- `entities.py:32477` (context key) and `ci-watch.sh` fixtures (`recheck-gate` in
  head lists) need updating.

### Totals

| | tests.yml ids | PR check rows | PR wall clock (median run 2059 s) | push run (median 2963 s) |
|---|---|---|---|---|
| (a) | −5 (`nightly.yml` gets those 5 plus a copy of `nightly-ha`, which keeps its PR arm in tests.yml) | −5 | 0 | 0; `record-autofix` (119 s) leaves the Tests push run (D-1) |
| (b) | −1 | −1 | −16 s execution and queue, on pin-chain PRs only | 0 |
| (c) W1 | −1 (`composed-proof`) | −1 | median −232 s to −342 s (bare cost 480 s to 239.1 s); 2 of 24 runs slower, by up to 404 s | 0 (`closures` stays under `fast`) |
| (d) | −1 | −1 | 0 | 0 |

tests.yml: 27 → 19 ids; nightly.yml: 6.

## 3. Required checks

**No rename. No ruleset edit.** The seven tests.yml contexts keep their job ids and
shape:
- `fast (3.14)`: the matrix and step-level skip are untouched.
- `browser`, `briefs`, `closure-scope`, `closures`, `typing`, `mutation`.

Each still runs on `merge_group`, which `entities.py:28003-28036` re-asserts.

Constraints on the implementation:
- **Never put a required id in nightly.yml.** A schedule run's check of the same
  name lands on main's commit, not the PR's, so it is harmless. But
  `entities.py:27701-27715` maps contexts to producers across workflows by id, and
  a second producer is a second reader.
- **Never give a tests.yml job a `name:`.** That renames the check.
- **`cancel-superseded` already collides with `codeql.yml:100`.** Not required, so
  harmless. Left as is: renaming it is a reader churn of `_NS_OVERRIDES` and
  `_PRW_SUBJECTS` for no saving.

## 4. Migration: PR 1

Authored by `hpo-author` (`tools/pr/app_push.sh`). The policy-text edits make it a
policy PR: owner approval by review before merge, and code-owned throughout. PR 2
(DESIGN-P2.md) follows it; it is not a dependency of anything here except the stub.

**The diff:**
1. `.github/workflows/tests.yml`: sections 2(a)–(d). Rewrite the header comment
   (lines 1-102) to name the Nightly split, and the concurrency comment's
   recheck-gate sentence.
2. `.github/workflows/nightly.yml` (new) and `.github/actions/nightly-ha/action.yml`
   (new).
3. `tests/nightly_status.py`: `DEFAULT_WORKFLOW`, the dispatch message, the
   docstring. `REQUIRED_LANES` unchanged.
4. `tests/entities.py`: every reader in section 1 of a moved or removed job;
   `_NIGHTLY_YML`; the composite-action reader; the `always()` pin on
   `mutation`'s plan step; the C1 pins removed and the no-C1-token pin added
   (2(c)); the stub pin below.
5. `tests/closure.py`: `GATE_FILES` += the two new files and the stub, less
   `composed_proof.sh`; the C1 code (2(c)).
5a. W1 (2(c)): `tools/coverage/coverage_tree.sh`, `tests/derive_closures.sh`;
   `tests/composed_closures.json` and `tools/coverage/composed_proof.sh` deleted;
   then `python3 tests/closure.py prune` for the three phantom entries.
5b. The inert `.github/workflows/ci.yml` stub: `name: CI`, `on: workflow_dispatch`
   (inputs `pr`, `base`, `recheck`, `no-skip`, all optional strings, so PR 2's
   dispatches already validate), `permissions: {}`, and one job `stub` that runs
   `true` with `permissions: {}`. `workflow_dispatch` only dispatches a file that
   exists on the default branch, so without it no `probe/ci-layout-<unit>` ref can
   dispatch the umbrella and PR 2's fan-out cannot run (DESIGN-P2.md section 10).
   `entities.py` pins it inert: no other trigger, no job but `stub`, no grant, no
   `uses:`. It writes no check at any PR head (dispatch only, and nobody dispatches
   it on a PR branch until PR 2 replaces it).
6. `tools/pr/merge_main_bot.py`: PIN_CHAIN and its self-test.
7. `tools/audit/seat/merge_train.py:2971-2975`: self-test path.
8. `tools/policy/policy_lint.mjs`: REPORTER_INPUTS += nightly.yml.
9. `tools/audit/seat/ci-watch.sh`: fixtures naming `recheck-gate` (cosmetic, but they
   are a reader).
10. `.github/CODEOWNERS`: `/.github/actions/ @tvofi`.
11. Policy and record: `ci-autofix.md`, `defect-root-cause.md` (:143 and :146),
    then `node tools/policy/rules_sync.mjs` and `--check`; `HANDOVER.md`;
    `tests/README.md`.
11a. `dev/audit/harnesses/r10_replay_loopnorm.py`: read `slow` from `tests.yml`
    and `nightly.yml` runs (2(a)).
12. `tests/closures.json`: **not edited by hand.**

**Closures, on Linux, in CI only.**
- tests.yml is a gate file, so this PR runs `MODE: FULL` and `closures`' full arm
  re-records every script under `strace` on the Ubuntu runner.
- The three closure entries naming W1's deleted files are phantoms: run
  `python3 tests/closure.py prune` and commit its result before the push
  (`ci-autofix.md`: the autofix cannot drop a dead path).
- `entities.py`'s closure gains the new files. `closures` prints UNDER-SCOPED,
  and `closures-autofix` pushes `ci: re-record closures` from the Linux recording.
  Wait for that commit, and read its summary line, not the tick (`ci-autofix.md`).
- **No seat runs `tests/derive_closures.sh` on Darwin** (`gate-scoping.md`).
- If `closures-autofix` goes red, the fallback is a Linux `--single tests/entities.py`.

**The null control has two halves** *(rev1, item 9)*. Phase 1's step-set half saw
only steps that executed in the sampled runs, so a deleted job or step that the
sample skipped, or a step body gutted under its old name, passed it: the review seat
planted all three and both phase 1's `stepset.py` and phase 2's `unitcheck.py`
returned 0 (review `ev/plant_unitcheck.txt`).

**Static half, `measure/rev/unitcheck2.py static`.** It parses the workflow files
before and after and compares, per job, one row for the job's own keys (`if`,
`needs`, `permissions`, `environment`, `strategy`, `outputs`, `runs-on`, timeouts,
`env`, `concurrency`, `name`, …) and one row per step keyed by name, hashing `run`,
`uses`, `with`, `if`, `env`, `shell`, `id` and the rest; plus a file-level `|floor`
row (top-level `permissions`/`env`/`defaults`) and a `|triggers` row. Every step
counts whether or not a run executed it. A closed map lists the intended `renames`,
`dropped`, `gained` and `changed` rows; each admitted `changed` row is printed before
and after, so the reviewer reads exactly the edits the map lets through. Its
self-test (`measure/rev/unitcheck2_selftest.txt`, over main's `tests.yml`): the file
against itself and a key-order reserialisation pass; the review's three plants (a
job deleted, every conditional step of `fast` deleted, a `closures` step gutted)
and a changed `if:`, a widened job grant and a widened file floor each fail; a
mapped drop and a mapped change pass. `SELF-TEST ok (12/12)`.

For PR 1 BEFORE is main's `tests.yml`; AFTER is
`tests.yml+nightly.yml+.github/actions/nightly-ha/action.yml` at the PR head, whose jobs the instrument merges into one mapping. The one id both workflow files hold,
`nightly-ha`, keeps its key in `tests.yml` (the PR arm, a `changed` row) and is keyed
`nightly:nightly-ha` in `nightly.yml` (`gained`). The map:

```
renames:  mutation-pin-plan|Size the shard matrix from the sites the diff added
            -> mutation|Size the shard matrix from the sites the diff added
dropped:  every mutation-pin-plan row but the rename; recheck-gate (all rows);
          composed-proof (all rows);
          coverage|<the composed-closures upload>; coverage|Check the restored coverage is main's push run's;
          closures|<the three composed fetch / verify / stage steps>
changed:  |triggers; |floor (none expected: tests.yml keeps contents: read);
          fast| browser| briefs| typing| coverage| coverage-ratchet| mutation| (the job `if:`
          and `needs:` losing recheck-gate; mutation gains `outputs:`);
          closures| (needs loses coverage); nightly-ha| (PR arm only);
          fast|<the drift-cache steps whose if: names recheck-gate>;
          closures|<the tree-hash write and tree-named upload, dispatch arm only>
changed:  mutation-nightly| mutation-ledger| mutation-ledger-push| slow| record-autofix|
          (each moved job's `if:`/`needs:` edit; a verbatim move keeps every key,
          so its steps show nothing at all)
renames:  nightly-ha|<each step> -> action:nightly-ha|<the same step>
          (AFTER is tests.yml+nightly.yml+.github/actions/nightly-ha/action.yml; the
          instrument reads a composite action's steps as the pseudo-job
          `action:nightly-ha`, so a step moved verbatim shows nothing)
gained:   nightly-ha|uses:./.github/actions/nightly-ha and the same in nightly:nightly-ha;
          every other nightly:nightly-ha row
```

A fixer enumerates the `<…>` rows exactly from the before file; anything the map does
not list fails.

**Runtime half, `measure/p1/stepset.py`, kept,** with the refusals of
`unitcheck2.py runtime`: each pair must match event, sender class (App push,
`github-actions[bot]`, human) and scoping case, read from the saved run listings,
or the comparison refuses (exit 2) rather than compares. Its controls (phase 1, run
again by the review seat, `ev/rerun_p1_stepset.txt`):

| control | runs | result |
|---|---|---|
| null: one run against itself | 39158277850 vs 39158277850 | `before 88 after 88 lost 0 gained 0` |
| perturbation: same PR (#2420), two App-sent heads; `cancel-superseded` ran at one only | 39151687395 vs 39158277850 | `gained 2` (`cancel-superseded`), rc 1 |
| perturbation: a pin-chain run against a plain one | 39148893518 vs 39158277850 | `lost 16 gained 2`, rc 1 |

Its map is the static map's step rows, less the `changed` rows (a runtime step set
has no bodies).

| case | before (main's layout) | after (this PR's layout) |
|---|---|---|
| ordinary scoped PR | a recent App-sent `pull_request` run, e.g. 39158277850 | the same diff re-pushed by the App onto a throwaway branch stacked on this PR's head; the `pull_request` run there |
| PR touching tests.yml (FULL) | an App-sent `pull_request` run on main's layout that touched tests.yml | **this PR's own run** |
| autofix-style dispatch | a recheck-arm dispatch, e.g. 39158300302 | `gh workflow run tests.yml --ref <throwaway branch> -f recheck=true` by the same identity |
| pin chain | 39148893518 | **not reproducible on demand** (needs a mutation refusal); see risk R-2. The static half covers its wiring before the merge |
| nightly | schedule run 39106988523 | after merge: the dispatched Nightly run on main (a `workflow_dispatch` pair needs a dispatched BEFORE: dispatch `tests.yml` on main before the merge, `-f recheck=false`) |

Merge rule: the static half passes under the map, and every runtime row except the
pin chain and the nightly shows `STEPSET … lost 0 gained 0` under the map before the
merge. The nightly row and the pin chain are checked after the merge, with a revert
ready.

## 5. Risks, and what could not be measured

- **D-1: `record-autofix` out of Tests. Owner ruling: approve.**
  - Moving it means a delivery-row beat failure no longer makes main's Tests run
    red. 2 of 5 measured push runs were red for this reason alone; the review seat
    read both as operational (`RECORD AUTOFIX: skip-push-refused`, `HTTP Error 403`).
  - `stamp.py` loses no protection: its rule 2 reads `--event push` runs of Tests
    (:1413-1415) and rule 5 re-applies the record predicate itself through
    `delivery_status.py --require-rows` (:34-38). `merge_train.main_green` waits on
    required contexts only (:1415).
  - The tick still sees a red `record-autofix`: it reads per-commit check runs
    (`orchestrator_tick.py:296-305`) and NIGHTLY_CLASS matches `record` (:168,
    :921-925). The review seat confirmed this reading.
  - **The refused branch, kept specified** *(rev1)*: `record-autofix` stays in
    tests.yml with its `environment: record-writer` and its App secrets, and
    tests.yml keeps `schedule:` (the one cron) and its `push` arm for it alone.
    Every other remaining tests.yml job's `if:` gains `github.event_name !=
    'schedule'`, because `closures` (`!cancelled()`) and `coverage` would otherwise
    still run nightly; `nightly.yml` then carries 5 jobs and no `push` trigger. The
    static map gains `changed` rows for each of those `if:`s. Section 2(a)'s other
    moves, (b), W1 and (d) are independent of this. DESIGN-P2.md section 5 states
    what the refused branch means for the umbrella.
- **R-2: the folded pin-plan cannot be exercised before merge** without a PR whose
  `mutation` refuses. The defence:
  - the `entities.py` wiring checks (`always()`, `needs.mutation.outputs.shards`);
  - the static null control, whose map admits exactly `mutation|`'s new `outputs:`
    and the renamed plan step, and prints both before and after (section 4);
  - a live check on the next refusing PR: 2 of 20 PRs measured, about one a day at
    today's rate.

  A wrong wiring shows as `mutation-pins` failing at matrix expansion. The cost is
  one autofix cycle. Separating (b) into its own PR removes this risk; the plan
  keeps two PRs in all, so (b) rides in PR 1.
- **R-3: the Nightly ledger pair runs only on main.** `mutation-ledger` and
  `mutation-ledger-push` are ref-guarded to main, and `workflow_dispatch` needs the
  file on the default branch. Their first execution under nightly.yml is therefore
  post-merge.
  - The `ledger` environment is branch-scoped, not workflow-scoped. Not verified
    against the environment's settings: the environments API is closed to both
    seats that tried (review `ev/environments_live.json`). **Owner action before
    the merge:** confirm that the `ledger` and `record-writer` environments'
    deployment-branch rules admit `main` and name no workflow file.
  - The `pool-seconds-*` cache is repository- and branch-scoped, so a new workflow
    restores it. That is GitHub's documented behaviour; not measured here.
- **R-4: nightly-status red window** after the merge, described in 2(a). It is
  non-blocking by construction.
- **R-5 (rev1): W1 reverses a round-9 decision (owner ruling D-4: drop).** At the
  measured bare cost (221-480 s on CI) the PR median gains 232-264 s, 2 of 24 runs
  are slower by up to 351-404 s, and V2 would gain a median 343 s while keeping
  C1 (2(c), `measure/rev/c1_sweep.txt`). The proof C1 needed is covered by the
  composition's removal at its source (2(c)).
- **Withdrawn (was R-5): `composed-proof`'s nightly arm becoming the self arm.**
  The job is deleted with W1; there is no nightly arm and no self arm.
- **Not measured:**
  - **Queue time across workflows.** A second scheduled workflow competes for the
    same runner pool at 02:17. The night's runner total falls, so this should not
    worsen.
  - **Fork PRs and `merge_group` runs.** None appear among the 20 runs, and merge
    queue runs were not sampled.
  - **The 10 PR runs where `cancel-superseded` is absent** rather than skipped,
    which are older bases. Not used.
  - **Whether any out-of-tree seat script** (`SEAT-BLOCK.md` and similar) names
    the moved jobs. Only the tree was searched.
  - **Billing rounding.** If the repository is private, each removed job saves up
    to a rounded minute. Visibility was not checked.
