R10-OUTSIDE-INTAKE part 2: the plan-page closure rule, the Flow section and the bottleneck alert. This is the group's part 1 (#3262) follow-on, built from the prototype at `handoff-wip/r10-outside-intake-p2` (`a37a13bf`) and continued from it, fast-forward only.

The owner, verbatim (tvofi 2026-11-07): "1: groups with all it's carries absorbed by another group should be considered closed, if that is not unsound for some reason. 2: Add flow board metrics in the plan HTML and a mechanism to alert you [the orchestrator] on bottlenecks and enable you to decide whether to act on it. Build it locally first and have the public plan page group land it on main."

**A workflow and the sweep template change: this needs tvofi's approving review** (`.github/workflows/governance.yml` gains one self-test step; `tools/audit/seat/sweep_template.md` gains the `train_log` placeholder and one sentence on what a `BOTTLENECK:` line asks of the sweep).

**Carry 1** (roster `R10-OUTSIDE-INTAKE`, part 2) is discharged by this pull request in full:
- the closure rule and the record-lag writer (items 1-2 below);
- the flow metrics, the alert and the beat row with `--train-log` passed (items 3-5);
- every mutant it owed (under Mutation proof);
- the disposition of `r10_plan_page_mutants.py` M0, which is repaired (item 6).

What lands:

1. **Closure rule (proposal 1).** `roster_lib.discharged`: a group at `carries-open`, with a merge sha in `resume.commit`, that owes no carry (every carry is marked implemented, moved or dismissed, or is legacy at the cut-over). Any other stage is never discharged, because the group's own brief is undone. `replan.dependency_graph` counts a discharged group done, so it takes no slot, pays no batch and clears its after-edges. `plan.json` gains a per-group `discharged` flag and `summary.groups_discharged`. The roster stage is not rewritten. `plan_page.py` renders a discharged group as merged, labelled `every carry discharged; record owed: close or re-own #..., then set-stage done`.
2. **The record lag, closed at its writer.** `roster_edit.py mark-carry`: when a mark discharges the last pending carry of a `carries-open` group, it applies set-stage done's own closing rule (`roster_lib.closing_stage`, then `hold_done`'s `carry_audit.orphaned` test). It writes `done`, or keeps the group `carries-open`, prints `HELD` and names each open issue that holds it (`close_discharged`). No beat writes `set-stage done`, because the orphan rule would hold it anyway.
3. **Flow metrics (proposal 2).** These are computed in `tools/audit/merge_throughput.py` and imported by the page and the alert, never copied. They are `flow_merge_wait`, `train_batches`/`read_train_batches` and `bottleneck_metrics`, which composes them with `flow_closed`, `flow_verdicts`, `flow_lead` and `pr_cap.wip_groups`. `plan_page.py` draws a Flow section after the issue chart, and takes `--train-log` and `--no-flow`. The tip also carries the prototype's mobile layout and the issue projection read through `fixes`.
4. **The alert.** The new `tools/audit/seat/bottleneck_check.py` prints `BOTTLENECK: <metric> <value> vs <threshold> -- <suggested action>` per breach and nothing on success. A source it cannot read gives `BOTTLENECK-UNREADABLE: <metric> -- <why>`. It suggests, and the orchestrator decides. The thresholds and minimum samples are the owner's (`THRESHOLDS`). Throughput keeps `flow_closed`, which counts roster closes rather than merges. The instrument doc says so, and says that a hand record batch reads as a burst.
5. **The beat.** `beat_jobs.py` gains a `bottleneck` row after #3262's `outside-intake`, in `ROWS`, `RUN` and `beatd.jobs.json`, every 1800 s. It runs with the beat checkout, the overlay's new `train_log` key, the `plan_slots` cap and `--memory state/bottleneck.json`, so a held breach is new once per trip. A missing key or a failed check is UNREADABLE. `plan-beat` hands `train_log` to `state_docs.py`, whose new `--train-log` passes on to `plan_page.py`, so the page's skip-share and train-skips table read the live log.
6. **r10_plan_page_mutants.py M0: repaired.** At main `17e621f08`, M0 printed `verdict=null`. On the prototype it failed, because the state_docs self-test check "a fresh plan draws PLAN.html in the plan table's commit" required `"UNAVAILABLE" not in good`, and the Flow section's UNAVAILABLE metric cells are in a healthy page. The check now keys on `PLAN UNAVAILABLE`, the refusal page's own heading, as `draw_plan_page`'s crash guard already does. M0 prints `verdict=null` at this head. The design choice (`fixer.md` step 11): a drawn page may carry an UNAVAILABLE metric, and only the refusal page is the UNAVAILABLE page.

Alternatives, and why each lost (`fixer.md` step 17):
- **Rewriting the roster stage to `done` from the plan, or from a beat.** `roster_sync.hold_open` and the done hold keep a group `carries-open` while it owns an open issue nothing else owns. A writer that bypassed that would orphan the issue. The plan only views the group as closed, and the roster's one closing writer (`_closing` plus `hold_done`) is reused by mark-carry.
- **Marks-aware pricing of partly discharged groups** (open carries = the min of the measured count and the unmarked count). The roster carry measured it at 0 h of closure movement, so it is not built.
- **Copying the flow computations into the page or the alert.** That would create two owners of one metric, so both import `merge_throughput`.
- **Throughput from group merges.** It would add a second throughput definition beside the flow board's, so it is deferred and documented. The roster's write time is the flow board's rule.

## Head

Repair round at `b99248e2bfb3023d2badd7c4a4a3ed63a479864d` (the `closures-autofix` bot's `ci: re-record closures`). The dispatch seat read four reds there (`tests / closures-autofix`, `tests / coverage-ratchet`, `tests / graders-head-copy`, `tests / lane-proofs`) and the cancelled run 42529990775. None is a failure: each is `conclusion: cancelled` in run 42529990775 (event `workflow_dispatch`, attempt 1), superseded at the same head by run 42529995793 (event `pull_request`, attempt 2, released by `hpo-runs`). No check-run at `b99248e2` carries `conclusion: failure` (read from the PR's check-runs 2026-11-08T23:16Z), so there is no branch-caused red to repair and no production or test line changes.

`f10cb23fbdf0ca57ecdf784665699b29e463a109` is the new head: `b99248e2` plus a merge of `origin/main` at `425b858495432c8dceb89d8d13866550352ba54f` (read 2026-11-08T23:22Z), taken because main had moved since the last prepr run. `git merge-tree --write-tree origin/main b99248e2` reported no conflict. Main's side touches one file this branch also changes, `tools/audit/seat/roster_edit.py` (auto-merged); its self-test and the owed-mutant harness were re-run at the new head (Figures). Figures without a commit named were taken at `f10cb23fb`.

`2fb9b2467dd625dbadcd0bab5cb6c5b3e09fdb04` is the head handed off: `f10cb23fb` plus a clean merge of `origin/main` at `fdc8d21adaa50a7feee534f08ee5edde9bda81ed`, which moved during the first prepr run. That merge touches `dev/governance/roles/fix-review.md`, `dev/programme/delivery/3338.md`, `tools/audit/seat/cloud_dispatch.py` and its instrument doc (`git diff --name-only HEAD^1 HEAD`), none of them this branch's, so the `f10cb23fb` self-test and harness figures describe the same branch files. The scoped gate, `tests/structure.py`, the claims check and prepr were re-run at `2fb9b2467`. The merge base is `fdc8d21ad`.

## Mutation proof

`python3 dev/audit/harnesses/r10_outside_intake_p2_mutants.py` (in-tree) runs every mutant the carry owes. It applies one replacement, runs the mutated file's own `--self-test` (beat_jobs with `--no-mutants`), and restores the file through `mutant_guard`. At `f10cb23fb` it printed `RESULT survived=0`, every mutant `verdict=killed`:

- `roster_lib.discharged`, one per conjunct: `discharged-any-stage`, `discharged-no-commit`, `discharged-any-commit`, `discharged-carries-ignored`, `discharged-legacy-ignored`, each killed by its named roster_lib self-test case ("an unmerged group's own work is undone", "carries-open with no recorded merge is not", "one unmarked carry keeps it owed", "a legacy carry is not owed").
- **replan:** `replan-discharged-arm` (3 FAIL lines) and `replan-legacy-dropped` (2).
- **flow_merge_wait:** `wait-after-merge-verdict` (3) and `wait-at-head` (2); the latter is killed by "merge-wait: a verdict on another head is read, not at head".
- **train_batches:** `train-done-flag` and `train-skip-first-batch` (2 each).
- **plan_page:** `page-discharged-label`, `page-done-set` and `page-merged-set`, each killed by "discharged: rendered merged, naming the record step it owes".
- **The beat row:** `beat-memory-dropped`, `beat-rc-clean`, `beat-unreadable-dropped`, and `beat-missing-key-runs` (killed by "bottleneck: an overlay without train_log is UNREADABLE and runs nothing"). beat_jobs' own `MUTANTS` carry four more kills: `bottleneck_memory_dropped`, `bottleneck_rc_clean`, `bottleneck_unreadable_dropped`, `plan_train_dropped`.
- **mark-carry closing arm:** `mark-close-off` (2), `mark-close-any-stage` (killed by the in-progress null-control case) and `mark-close-no-hold` (killed by the held case).
- **bottleneck_check's own 10 rule mutants:** every one is killed (`ok: bottleneck_check self-test`).
- **The state_docs `--train-log` hand-on.** Removing `"--train-log", str(train)` from the self-test's argv fails "plan page: --train-log reaches plan_page.py: the page's train skips name its batch"; restoring it passes (taken at `78d409286`).

## Null control

- Harness M0, nothing replaced, runs all six self-tests and prints `RESULT mutant=M0 rc=0 fails=0 verdict=null` at `f10cb23fb`, so every kill above belongs to its mutant.
- `r10_plan_page_mutants.py M0` printed `verdict=null` at main `17e621f08` and `verdict=SURVIVED` (1 FAIL, the state_docs check above) at `f34f6ec84`; `verdict=null` at `b87da1699`.
- For the replan figures, the base arm is main's own `replan.py` (`git archive origin/main`) on the same roster and the same `--start`. Its `groups_discharged` key is absent, and it schedules every group.
- The mark-carry arm has two null controls: a last mark on an `in-progress` group leaves its stage; a mark that leaves one carry pending keeps `carries-open`.
- Repair round: the claim "no red at `b99248e2` is a failure" is read from every check-run's `conclusion` field on the PR's check-runs listing; had any job failed, its row would read `failure`, as the four named rows read `cancelled` and the live run's completed rows read `success` or `skipped`.

## Figures

- **Replan, both arms** (taken at `78d409286`). Command: `python3 -I <tree>/tools/plan/replan.py --repo . --roster-ref origin/handoff/audit-r10-roster --start 2026-11-08T20:20:00Z --slots 20 --seats 20 --out plan-<arm>.json`. `<tree>` is `git archive origin/main` (the base, at main `17e621f08`) or `git archive` of this branch at `78d409286`. The roster was `origin/handoff/audit-r10-roster` at `fcc9a1933aa1`, read 2026-11-08T20:20Z. Read from `summary` and `groups[*].discharged`:
  - base: closure 2026-11-15T07:03:00Z, 49 batches, 6075.0 CI minutes, 324 done / 71 open.
  - head: closure 2026-11-15T07:03:00Z, 48 batches, 5962.5 CI minutes, 327 done / 68 open, `groups_discharged` 3.
  - The 3 groups are R10-CI-GRADER-BATCH-STUDY, R10-FRICTION-CI-RED and R10-FRICTION-OTHER-FAMILY, each `carries-open` with a recorded commit and no carry. Their wired issues are none, #3156, and #3283 #3313 #3314 respectively; the first owes only `set-stage done`.
  - The critical path is identical in both arms: R10-GENERIC-HEAT-CURVE, R10-GENERIC-HEAT-CURVE-PERSISTENT, R10-ARBITER-OFF-RESTORE, R10-ARCH-DOCS, R10-CLOSEOUT-CLEANUP, so the closure date does not move on this roster.
  - The figures are a function of the roster tip and `--start`; on another roster, re-run the same command rather than carry them.
- `python3 dev/audit/harnesses/r10_outside_intake_p2_mutants.py` at `f10cb23fb`: every mutant line `verdict=killed`, M0 `verdict=null`, `RESULT survived=0`.
- Self-tests at `f10cb23fb` (`python3 -I <file> --self-test`), the files main's merge reaches:
  - `tools/audit/seat/roster_edit.py`: `roster_edit self-test: 260 checks, 0 failed` (main added cases; it read 246 at `b87da1699`).
  - `tools/audit/seat/roster_lib.py`: `roster_lib self-test: 72 checks, 0 failed`.
  - `tools/audit/seat/r10_roster_ops_mutants.py`: `r10_roster_ops_mutants self-test: 321 checks, 0 failed`.
- Self-tests at `b87da1699`, untouched by the merge: `replan.py` `self-test: 0 failed`; `merge_throughput.py` `ok: merge_throughput.py self-test`; `plan_page.py` `plan_page self-test: 75 checks, 0 failed`; `bottleneck_check.py` `ok: bottleneck_check self-test`; `beat_jobs.py` `beat_jobs self-test: 185 checks, 0 failed`; `state_docs.py` `state_docs self-test: all checks passed`; `beatd.py` `beatd self-test: 119 checks, 0 failed`; `hooks_setup.py` `hooks_setup self-test: 39 checks, 0 failed`; `sweep_render.py` `sweep_render self-test: 34 checks, 0 failed`. The harness above re-runs six of them unmutated (M0) at `f10cb23fb`.
- `python3 tools/audit/seat/selftest_wiring.py --check` (at `b87da1699`): `125 self-testing, 125 wired, 0 unwired`. Before the governance.yml step it printed `UNWIRED tools/audit/seat/bottleneck_check.py`.
- **Gate scope.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` at `2fb9b2467` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`; `scope.run` names `tests/entities.py` and `tests/harness_headers.py`.
- **Scoped scripts**, with `PYTHONPATH=tests/hastub`, at `2fb9b2467`:
  - `tests/entities.py`: `ALL 2668 ENTITY CHECKS PASSED`.
  - `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - The `run_always` lines: `tests/env_drift.py --claims-only` printed `claims hygiene: origin/main ok`, and `tests/closure.py selftest` printed `ALL 118 closure shrink pins PASSED` (at `f10cb23fb`).
- `python3 tests/structure.py` at `2fb9b2467`: `STRUCTURE RATCHET PASSED`. No `*_budgets.json` is in the three-dot diff.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- `VERSION`, `RELEASE_NOTES.md`, the manifest and both claim files are untouched by the three-dot diff. No golden was run, because the diff touches none.
- Toolchain: `bash tools/audit/seat/cloud-setup.sh --check` printed `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` at `f10cb23fb`: `PRE-PR: f10cb23fbdf0ca57ecdf784665699b29e463a109 0000000000000000000000000000000 rc=0`; at `2fb9b2467`: `PRE-PR: 2fb9b2467dd625dbadcd0bab5cb6c5b3e09fdb04 0000000000000000000000000000000 rc=0`; `origin/main` unmoved at `fdc8d21ad` since that run, so no third merge.

## Red checks

At `b99248e2`, each red and cancelled check by name; none is a failure the branch caused:
- `gate` (run 42529990775): `cancelled`. Its run was superseded at the same head by run 42529995793 (`cancel-superseded`, the `pull_request` attempt `hpo-runs` released). Cheaper detector: none exists; a cancellation is not a defect.
- `tests / closures-autofix`, `tests / coverage-ratchet`, `tests / graders-head-copy`, `tests / lane-proofs`, `tests / ci-ratchet`, `tests / claims-autofix` (run 42529990775): `cancelled`, the same supersession. Cheaper detector: none exists, as above.
- `tests / fast (3.14)`, `tests / coverage`, `tests / closures`, `governance / instrument-self-tests`, `codeql / Analyze (python)` (run 42529990775): `cancelled` by the same supersession; in run 42529995793 at the same head `tests / fast (3.14)` and `governance / instrument-self-tests` completed `success`, and the other three were still running when read (2026-11-08T23:16Z). Cheaper detector: none exists.
- `tests / closures` was red earlier on this PR as UNDER-SCOPED (predicted in the previous body: `plan_page.py` imports `merge_throughput.py` and `bottleneck_check.py`), repaired by the `closures-autofix` bot commit `b99248e2` (`ci-autofix.md`). Cheaper detector: `ci_predict.py` (prepr step 6d) is it, and it ran before the handoff; `PREPR_SKIP_CLOSURES=1` leaves the re-derivation to the bot by design.

At `2fb9b2467` no check has run yet.

## Unpinned sites

none: prepr's unpinned-sites step reported `the diff adds no unpinned mutation site`.

## Forward-carry

none

## Friction

- brief: stale: the repair brief reads four `cancelled` rows of a superseded `workflow_dispatch` run as "real reds, not gate deferrals"; every one is `conclusion: cancelled` and the same head's `pull_request` run was live. Carry: dismissed: no stage's method changes; a cancelled row is read by its conclusion field, which this body records
- brief: stale: the roster carry says `r10_plan_page_mutants.py` M0 "fails on main as well as on this tip"; at main `17e621f08` M0 printed `verdict=null`, and only the tip failed (the Flow section's UNAVAILABLE cells), repaired here. Carry: dismissed: repaired in this pull request, and the carry is consumed by this landing
