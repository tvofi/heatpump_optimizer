R10-CI-LAYOUT-P2, sub-PR P2b ("cut-over"), unit **U9a**, the seat readers. Part of #2495.
Built offline against `tools/ci/gate.py` `REQUIRED` and `tools/policy/fixtures/required-contexts.json`
`gate_required` as merged by P2a (#2622, `a1633381a`). U0c's handoff ref was not published when this
unit finished (`git ls-remote origin 'refs/heads/handoff/r10-ci-layout-p2-*'` printed nothing), so the
names are gate.py's: `<stem> / <job>` plus `gate`. Design: DESIGN-P2 §9 at `1371a0a6`; PLAN.md A5 and
DESIGN-REVIEW A5/B3 at `1011d6b2f`.

## Head

Code head: `handoff/r10-ci-layout-p2-u9a` = `c9d647e64` (full SHA in the ref), four commits on origin/main `fef4a1351db3`
(contains P2a's merge `a1633381a`: `git merge-base --is-ancestor a1633381a origin/main` rc 0).
`git log origin/main..HEAD` holds only this unit's four commits (`77f97545c` the readers, `704775476` a ci_ratchet self-test arm, `0936e57c3` the harness's root walk, `c9d647e64` two INERT READS entries from `ci_predict.py --apply-inert`); no roster branch is merged. origin/main moved to `cf01e82ee` after the measurements (read at the push, `date -u` 2026-10-22); every figure here is at base `fef4a1351db3`, and fixer.md step 6 re-runs them after any merge.

## Unit

U9a, the seat readers. `git diff --stat origin/main...HEAD`:

```
 dev/audit/harnesses/r10_seat_selftests_mutants.py |  27 ++-
 dev/audit/harnesses/r10_u9a_ratchet_nulls.py      |  96 ++++++++++
 tests/ci_ratchet.py                               | 159 +++++++++++++++--
 tests/closures.json                               |   2 +
 tools/audit/seat/autofix_statuses.sh              |  16 +-
 tools/audit/seat/ci-watch.sh                      |  51 +++++-
 tools/audit/seat/merge_train.py                   | 208 ++++++++++++++++++++--
 tools/audit/seat/orchestrator_tick.py             |  52 +++++-
 tools/audit/seat/proof_watch.py                   |  59 +++---
 tools/pr/merge_main_bot.py                        |  50 +++---
 tools/release/stamp.py                            | 145 ++++++++++++---
 11 files changed, 742 insertions(+), 123 deletions(-)
```

Production against self-test lines (the added lines inside each file's self-test function, or a
harness, counted as test): about 305 production and 435 test (the split is a line classification by function, not a measurement CI repeats). The unit bound is about 400 production.

| file | change |
|---|---|
| `tools/audit/seat/merge_train.py` | `GATE`, `GATE_GREEN`; `latest_runs` reads `gate` per check suite, the worst suite standing (pending, then red, then green); `run_state` takes only `success` as a green `gate`; `gating_names()`; `platform_gate()` + `Train.cross_check()` (A5 item 3); `PR_ONLY = ()`; `DISPATCH = (("ci.yml", ("-f", "recheck=true")),)`; `--ignore-red` default `tests / nightly-status` |
| `tools/audit/seat/orchestrator_tick.py` | `PR_ONLY = ()`; MAIN's superseded and nightly/non-required classes read `mt.gating_names(req)` |
| `tools/audit/seat/proof_watch.py` | reads check runs through `merge_train.latest_runs` and `merge_train.classify` (its own `GREEN` and newest-wins loop deleted); fixtures `Tests` → `gate` |
| `tools/audit/seat/ci-watch.sh` | the red rule reads `gate` per check suite (5th TSV column `.check_suite.id`), red when a completed one did not succeed; gate fixtures W8-W12 |
| `tools/audit/seat/autofix_statuses.sh` | lists `ci.yml` pull-request runs; job names `tests / mutation-autofix`, `tests / closures-autofix`, `tests / closures` |
| `tools/pr/merge_main_bot.py` | `PIN_CHAIN = ^tests / (?:mutation\|mutation-pins(?: \(.*\))?\|mutation-autofix)$`; fixtures renamed, the tests.yml-id check maps `tests / <id>` |
| `tools/release/stamp.py` | rule 2 reads the `gate` job of HEAD's `ci.yml` push run (`gate_runs`, B3); the Tests push run is read only by `tests_run_fallback`, when HEAD has no `ci.yml` push run (the three-round fallback, isolated in its own function) |
| `tests/ci_ratchet.py` | `critical_path_minutes` via `run_minutes`: a `CI` push run from `created_at` to its last `tests / *` job's `completed_at`, a pre-umbrella `Tests` run as before; `--gather-runs FILE` writes the window (both workflows, newest 8, jobs embedded on each CI run); `script_runs` (the (c) `reused` exclusion) untouched |
| `dev/audit/harnesses/r10_seat_selftests_mutants.py` | per-file mutants inside each instrument's block (below); S16 re-keyed to proof_watch's new line; S36's pattern re-keyed to `handoff_push.sh`'s current line |
| `dev/audit/harnesses/r10_u9a_ratchet_nulls.py` (new, under `dev/audit/`, an `INERT` prefix of `tests/closure.py`) | the two ci_ratchet nulls below |
| `tests/closures.json` | two `inert_reads` entries written by `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main --apply-inert` (entities.py now reads proof_watch.py; harness_headers.py the new harness), never by hand; afterwards `CI PREDICT: no closures or fast red predicted against fef4a1351db3` |

## Interface

Consumed (P2a, as merged): `tools/ci/gate.py` `REQUIRED`; the fixture's `gate_required` (read, never
restated: `merge_train.REQUIRED_CONTEXTS`); the check-run name `gate`; units as `<stem> / <job>`;
gate.py's exit 3 `RATE-LIMITED` (a failed job). Consumed from U0c/U5: ci.yml calls tests.yml under the
job id `tests` (so `tests / mutation`, `tests / nightly-status`, `tests / closures-autofix`), `ci.yml`
takes `workflow_dispatch` with `recheck`, and its workflow `name:` is `CI` (stamp.py and ci_ratchet.py
also accept the file path `ci.yml`). If U0c publishes other names, `PIN_CHAIN`, `autofix_statuses.sh`,
`TESTS_JOB_PREFIX`, `CI_WORKFLOW` and the `--ignore-red` default re-key.

Exported:
- `merge_train.GATE = "gate"`, `GATE_GREEN = ("success",)`, `PR_ONLY = ()`, `DISPATCH`, `REQUIRED_CONTEXTS`.
- `merge_train.latest_runs(runs)`: as before for every name but `gate`; for `gate` the latest run of
  each `check_suite.id` is kept and the worst stands. A run with no suite id is its own suite.
- `merge_train.gating_names(required)`: `required` unchanged unless it holds `gate`; then
  `required ∪ gate_required`. **Departure from the brief, raised here:** the brief says
  `req = gate_required ∪ {gate}` for merge_train too. The train *decides* on the live ruleset's set
  (`{gate}`) and uses `gating_names` only to name reds, because deciding on `gate_required` would wait
  forever on `tests / coverage` (push-only, never at a PR head) and stop a merge GitHub takes when
  `arch-score / arch-score` is red off `custom_components/` (D-2: "arch-score reported, gate pass").
  The tick uses it exactly as DESIGN-P2 §9 item 11 says (classification of a red).
- `merge_train.platform_gate(payload, head) -> (green|red|wait|unread, why)` over `ROLLUP_Q`
  (GraphQL `statusCheckRollup.contexts` with `isRequired(pullRequestNumber:)`): green only when the
  contexts GitHub marks required are `gate` check runs alone, every one `COMPLETED` and
  `SUCCESS|NEUTRAL|SKIPPED` (GitHub's own passing set); another head's rollup or more than 100 contexts
  is `unread`. `Train.cross_check(pr, h)` runs it in the serial `ci` step once the train has read
  `gate` green, only when the live ruleset requires `gate`; anything but `green` is a `Stop("ci")`.
  One GraphQL call per landed entry.
- `stamp.gate_runs(payload, jobs_of)`, `stamp.tests_run_fallback(payload)`, `stamp.runs_path`,
  `stamp.jobs_path` (`actions/runs/<id>/jobs?filter=latest`), `stamp.get_gh`/`get_rest`; the
  `fetchers` injection of `tests_gate` now maps a source to a `path -> json` getter.
- `ci_ratchet.run_minutes(run)`, `ci_ratchet.gather_runs(file)` (`--gather-runs FILE`).

## Static map

This unit edits no workflow file. `measure/rev/unitcheck2.py static` (from `1371a0a6`), main's file
against this head's, with the empty map `{"renames":{},"dropped":[],"gained":[],"changed":[],"after":{}}`,
over every file `git ls-tree --name-only origin/main .github/workflows/` lists: rc 0 for all 16
(`arch-score`, `budget-raise-gate-rerun`, `budget-raise-gate`, `ci`, `codeql`, `governance`, `hassfest`,
`kernel-points`, `merge-main`, `nightly`, `pages`, `pr-contract-rerun`, `pr-contract`, `release`, `tests`,
`validate`); e.g. tests.yml `STATIC rows 174->174 lost 0 gained 0 changed 0 (mapped 0) misplaced 0 rc 0`.
The coordinator re-runs it against current main at assembly.

## Controls

Every plant below is a self-test check in the named file (run at `c9d647e64` under Python 3.13 with
`tests/requirements-ci.txt`), and every mutant is run by the seat harness or by hand as stated.

**A5, both heads, and the platform cross-check** (`merge_train.py --self-test`, 221 → 232 checks, 0 failed):
- head (i), an older red `gate` suite beside a newer green one: `classify` reads `red` (never green);
  head (ii), an older green beside a newer red: `red`. Null: two green suites read green, and a red
  attempt re-run green inside one suite reads green; a running suite beside a red one is a `wait`.
- `RATE-LIMITED` (a failed `gate` job, output title `RATE-LIMITED reset_epoch=1`), a `skipped` and a
  `neutral` `gate` all read red. Null: a skipped non-gate context still reads green.
- Layouts: an old-layout head (the fixture's 17 `contexts` green, no `gate`) under the `[gate]` ruleset
  is `wait` on `gate`, never green; a new-layout head (`gate_required` + `gate`) under the 17 waits on
  every old name, never green; the same head under `[gate]` is green.
- Platform: required gate runs all passing → green; an older failing suite → red; one in flight → wait;
  no required `gate` → red; GitHub requiring anything besides `gate` → red; a non-required red is not
  counted (null); another head's rollup, more than 100 contexts, or no rollup → unread.
- Serial train (`go()` world, ruleset `gate`): train green + GitHub green merges; train green + GitHub
  red (a suite the train never saw) stops; train green + unreadable rollup stops; head (i) stops at
  `red at the head` before any cross-check. Null: an old-layout ruleset makes no platform read and merges.
- `gating_names(["gate"])` holds `tests / closures` and `tests / ci-ratchet`; `["fast","closures"]` and
  `None` pass through unchanged.

Seat-harness mutants, `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py S16 S36 ci-watch-1
ci-watch-2 proof_watch-1 merge_train-19 merge_train-20 merge_train-21 merge_train-22 merge_train-23
merge_train-24 merge_main_bot-1 stamp-1 stamp-2 orchestrator_tick-5` at `77f97545c` (the three later
commits touch only `tests/ci_ratchet.py`'s self-test, the new harness and `tests/closures.json`, and the
harness was not re-run after them; every changed self-test was re-run green at `c9d647e64`):

```
== ci-watch-1 ci-watch.sh: KILLED rc=1 | ci-watch self-test: 13 checks, 1 failed
== ci-watch-2 ci-watch.sh: KILLED rc=1 | ci-watch self-test: 13 checks, 1 failed
== S16 proof_watch.py: KILLED rc=1 | proof_watch: REFUSE: --mode owner needs --mandate <comment-id>
== proof_watch-1 proof_watch.py: KILLED rc=1 | proof_watch: REFUSE: --mode owner needs --mandate <comment-id>
== S36 handoff_push.sh: KILLED rc=1 | handoff_push self-test: 2 checks, 1 failed
== merge_train-19 merge_train.py: KILLED rc=1 | merge_train self-test: 232 checks, 2 failed
== merge_train-20 merge_train.py: KILLED rc=1 | merge_train self-test: 232 checks, 1 failed
== merge_train-21 merge_train.py: KILLED rc=1 | merge_train self-test: 232 checks, 2 failed
== merge_train-22 merge_train.py: KILLED rc=1 | merge_train self-test: 232 checks, 1 failed
== merge_train-23 merge_train.py: KILLED rc=1 | merge_train self-test: 232 checks, 1 failed
== merge_train-24 merge_train.py: KILLED rc=1 | merge_train self-test: 232 checks, 1 failed
== merge_main_bot-1 tools/pr/merge_main_bot.py: KILLED rc=1 | merge_main_bot self-test: 41 checks, 7 failed
== stamp-1 tools/release/stamp.py: KILLED rc=1 | LEDGER-MERGE: tests/closures.json: text merge (a side is not in its writer's own JSON format)
== stamp-2 tools/release/stamp.py: KILLED rc=1 | LEDGER-MERGE: tests/closures.json: text merge (a side is not in its writer's own JSON format)
== orchestrator_tick-5 orchestrator_tick.py: KILLED rc=1 | orchestrator_tick self-test: 199 checks, 1 failed
RESULT survivors=0
rc=0
```

The step's last line is what the harness prints; where it is not the self-test's own tally (S16,
proof_watch-1, stamp-1, stamp-2) the self-test was run directly under the same mutant:
- S16 (`_, red, pending` swapped): `proof_watch self-test: 41 checks, 5 failed` ((g), (g2) ×2, (l) ×2).
- proof_watch-1 (newest-wins dict instead of `merge_train.latest_runs`): `38 checks, 2 failed`, both (g2).
- stamp-1 (`gate_runs` always `None`, so every HEAD takes the Tests fallback): 3 FAIL (the three B3
  checks that need the gate read), `RESULT stamp_self_test=fail`.
- stamp-2 (the run's conclusion instead of the gate job's): 1 FAIL ("the ci.yml push run's gate success
  is green, whatever the run concluded").

merge_train-19 is main's own `latest_runs` (newest wins for `gate`), so it is the failing-test-first
control for A5: 2 checks fail against it, heads (i) and the serial head (i).

**orchestrator_tick** (194 → 199, 0 failed): under `[gate]`, a red `gate` is `REQUIRED not green`; a red
`tests / closures` is never classed nightly/non-required; null: `record-autofix` (never owed by gate) is
still a non-required red, and a green gate with only `record-autofix` red reads the required set green.
`PR_ONLY == mt.PR_ONLY == ()`. orchestrator_tick-5 (`gating = req or []`): 1 failed.

**proof_watch** (36 → 40): (g) a red `gate` aborts naming it; (g2) an older red `gate` suite, and an older
RATE-LIMITED one, beside a newer green one abort with no merge.

**ci-watch.sh** (8 → 13): W8 green gate under `[gate]`, no alert (null); W9 an old-layout settled head
under `[gate]` alerts `ABSENT ... gate`; W10 older red suite + newer green alerts `RED: gate`; W11 a red
re-run green in one suite, no alert (null); W12 a skipped gate alerts `RED: gate`.

**merge_main_bot.py** (40 → 41): the renamed fixtures, plus W4: `tests / mutation-pins (1)` holds the
head and the pre-P2b bare `mutation-pins (2)` is not read (null). merge_main_bot-1 (prefix dropped):
`41 checks, 7 failed`.

**stamp.py** (187 → 194 ok lines): the CI push run's gate success is green whatever the run concluded; a
red push gate refuses naming it; RATE-LIMITED (failed), skipped, cancelled and absent gate jobs are never
green; a running gate is not green; once HEAD has a CI push run a green Tests run there does not stand in
for a red gate; fallback: a pre-umbrella HEAD is read off its Tests push run, and (null) refuses when that
run is red.

**ci_ratchet.py** (15 → 23, 0 failed; its self-test runs in tests.yml's `ci-ratchet` job, outside the seat
harness, so its mutants were run by hand from a clean copy, each restored):
- ci_ratchet-1, a CI run measured to its run's `updated_at`: 2 failed (got 120.0, want 40; window 85.0, want 45).
- ci_ratchet-2, CI runs not read: 4 failed.
- ci_ratchet-3, the `tests / ` prefix dropped: 3 failed (gate's 02:00 completion read: 120.0).
- ci_ratchet-4, the jobs-list refusal dropped: `FAIL a CI push run that carries no jobs refuses ... --
  crashed: TypeError` (the second commit makes that crash redden its own check instead of aborting).
- ci_ratchet-5, (c)'s `reused` exclusion dropped: the self-test stays green (that pin is
  `tests/entities.py`'s `_CIR_REUSE`, unchanged); the replay null below reads 73 under it.

**The two ratchet nulls**, `python3 -I dev/audit/harnesses/r10_u9a_ratchet_nulls.py [ci_ratchet.py]`:
- this head: `replay: closures 34, coverage fast 20, reused 19; arch pair counted: ['tests/arch_score.py',
  'tests/arch_score_head.py']`, `RESULT script_runs_per_push=54`, `RESULT critical_path_minutes=41.7333`.
- main's `tests/ci_ratchet.py` (`git show origin/main:tests/ci_ratchet.py`): the same three lines,
  `54` and `41.7333`.
- under ci_ratchet-5: `RESULT script_runs_per_push=73` (the 19 reused rows counted), so 54 is not a
  constant the replay prints.
The replay is a reconstruction, not a downloaded push run: the closures lane plan
(`tests/closure.py lane-plan --all-scripts`) plus coverage_tree.sh's `fast` DERIVED rule plus 19 reused
rows. The critical-path null is the last 8 tests.yml push runs on main as listed through the API at
2026-10-22T23:1xZ (one read; the newest still in progress, so 7 counted), stored in the harness.

**autofix_statuses.sh** (no self-test; one-off probe with a fake `gh` on PATH, not committed): a ci.yml
run whose jobs are `tests / mutation-autofix` + `tests / closures` reads `autofix jobs that ran: 1`,
`1 tests / mutation-autofix changed -`; the null, the same run carrying the pre-P2b bare
`mutation-autofix`, reads `autofix jobs that ran: 0`.

**Other checks at `c9d647e64`**: `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`;
`python3 -I tools/audit/seat/selftest_wiring.py --check` → `87 self-testing, 87 wired, 0 unwired`, rc 0;
`python3 tests/throwaway_git.py --check` → `0 raw git init or clone site(s) refused, 0 stale allow entries`;
`python3 -I tools/audit/seat/tmp_paths.py --check` → `0 refused, 0 stale allow entries`;
`tools/audit/archscore/score.py --diff <merge-base>` → `Architecture score: dS +0.0000 NULL`. No new push
site (`PUSHERS` unchanged). Scoped gate, `PREPR_SKIP_CLOSURES=1 GATE_SCOPE=auto PYTHONPATH=tests/hastub
./tests/run.sh` (the gate lease taken by run.sh itself), at `c9d647e64`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`, `ALL 2399 ENTITY CHECKS PASSED`, `ALL 109 HARNESS HEADER CHECKS PASSED`, `6 TEST SCRIPT(S) PASSED; 29 SCOPED OUT AND NOT RUN`, rc 0. The scope names `tests/doc_claims.py` and `tests/entities.py`; the rest is CI's (FULL on the assembled P2b). An earlier run at `0936e57c3`'s parent failed `harness_headers.py` on this unit's harness (`depth seams: ... parents[3]`), repaired in `0936e57c3`.

## Live checks owed

The coordinator's, on `ci-probe/all` (DESIGN-P2 §10, review A5/B3):
1. **A5 head (i)**: on the combined-control draft PR, an older red `gate` (a code run's) beside a newer
   green one (a review or edit run's) at one head, the sweep not yet run. `python3 tools/audit/seat/merge_train.py
   wait-ci <head>` and `classify <head>` read RED; the cross-check's GraphQL (`ROLLUP_Q`) read at that head
   must show the older suite's `gate` with `isRequired: true` and a non-passing conclusion. If GitHub
   instead marks only the newest `gate` required (the platform takes the newest), the train's per-suite
   reading is stricter than the platform: record it and refer it to M-2 (EXECUTION §5 decided the
   every-suite reading from #2009).
2. **A5 head (ii)**: an older green beside a newer red: both readers RED.
3. On both heads, `platform_gate` over the live rollup agrees with `classify`, and with
   `pulls/N` `mergeable_state` once the review rule is satisfied; a disagreement is a FAIL.
4. **RATE-LIMITED**: a `gate` that ended exit 3 is read red by merge_train, proof_watch, ci-watch and
   stamp (its job conclusion is `failure`).
5. **B3**: a planted red `tests / ci-ratchet` on a `ci.yml` push-shaped run reddens `gate` and
   `stamp.py --dry-run`'s rule 2 refuses naming `ci.yml push run's gate`; before the cut-over, `stamp.py`
   at main still answers from the Tests fallback.
6. **ci_ratchet**: the first `ci.yml` push run's `tests / ci-ratchet` job, given `--gather-runs`, reads a
   window mixing CI and Tests runs; `critical_path_minutes` over the last 8 old runs equals the old
   reader's (the harness above, re-run on the live listing).
7. **merge_main_bot**: a dry-run `merge-main` dispatch at a head whose `tests / mutation-pins (*)` are
   running prints `skip-pins-running tests / mutation-pins (...)`.

## Wiring

- `.github/workflows/tests.yml` (U5's file), job `ci-ratchet`, step "Fetch the recent push runs'
  durations": replace the `gh api ".../actions/workflows/tests.yml/runs?event=push&branch=main&per_page=8"
  > "$RUNNER_TEMP/runs.json"` line with `python3 -I tests/ci_ratchet.py --gather-runs "$RUNNER_TEMP/runs.json"`
  (env `GH_TOKEN: ${{ github.token }}`; `GITHUB_REPOSITORY` is the runner's). Without it a CI push run
  in the window carries no jobs and `run_minutes` refuses (fail closed), so the ratchet goes red rather
  than silently loose.
- No new self-test, so no `instrument-self-tests` step. No entities pin.

## P2a defect

none found in the P2a code this unit consumes (`gate.py` `REQUIRED`, the fixture's `gate_required`).

## Mutation proof

See `## Controls`: 15 seat-harness mutants, `RESULT survivors=0`, and 5 hand mutants of `tests/ci_ratchet.py`.

## Null control

See `## Controls`: the old-layout and single-suite nulls in each self-test, and main's `ci_ratchet.py`
reading `54` and `41.7333` on the same replay.

## Figures

- `script_runs_per_push=54`, `critical_path_minutes=41.7333`: `python3 -I dev/audit/harnesses/r10_u9a_ratchet_nulls.py`.
- self-test tallies: each file's `--self-test`, as listed under `## Controls`.
- `survivors=0`: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py <the 15 ids>`.
- `87 self-testing, 87 wired, 0 unwired`: `python3 -I tools/audit/seat/selftest_wiring.py --check`.
- production/test split: added lines inside each file's self-test function counted as test, a harness as test.

## Red checks

- `nightly-status`: red on main's ancestry (`tests.yml` `nightly-status`, which grades the nightly, not
  this diff); this unit changes no nightly input and no reader of `tests/nightly_status.py` (carry 9:
  the NEW/ABSENT window untouched). Not this unit's to answer beyond naming it.

## Forward-carry

- To the P2b coordinator (this body is its brief input): the **Wiring** line above for U5's tests.yml,
  and the uncertainty that the merge-main bot and `autofix_statuses.sh` read only the umbrella's names
  after the cut-over. Carry: P2b assembly (`plans/ci-layout/EXECUTION.md` §3, units into one P2b).
- To U9p (policy text): `nudge.md:93`'s stamp precondition becomes "the latest `ci.yml` push run's
  `gate` on the current `origin/main` is green", matching `stamp.py`'s rule 2 docstring here. Carry: U9p.

## Friction

- `brief-environment: cost: the cloud container's python3 is 3.11 without voluptuous; tests/entities.py
  needs 3.12+ f-strings, so the scoped gate needed a scratch venv (uv, python3.13, tests/requirements-ci.txt).
  Carry: the dispatch payload's setup line.`
- `r10_seat_selftests_mutants S36: stale: its pattern named handoff_push.sh's old push-open line, so S36
  printed NOT RUN on main; re-keyed here. Carry: this PR.`
