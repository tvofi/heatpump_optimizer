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

`b87da16993f1dff1bbbf7c8fae6de93bbcfcb515` is the head. It merges `origin/main` at `daf8b349f` (read 2026-11-08T21:13Z) into `3db23178b`. The merge was clean and touches only `tests/card_browser.mjs` and `dev/programme/delivery/3346.md`, neither of which is this branch's. The merge base is `daf8b349f`. The final prepr ran at this head. Where a figure below was taken at an earlier commit of this branch, the line names that commit.

The three commits after `16be6b8b8` (the merge of `51cd5ec8a`) are prepr repairs:
- `30c5d6b5a` re-anchors `tools/audit/seat/r10_roster_ops_mutants.py`'s H2 to the done-hold line that mark-carry's closing arm extended (`if closed or a.op == "set-stage" or ...`). Its self-test printed `r10_roster_ops_mutants self-test: 321 checks, 0 failed`. The same commit drops the owed-mutant harness's copy of the state_docs failure-summary grammar, so that grammar stays written once (the agreement lane).
- `86cca9a34` adds the two INERT READS that `ci_predict.py --apply-inert` wrote to `tests/closures.json`.
- `3db23178b` addresses the agreement lane, which read the prototype's `roster_lib._MERGE_SHA` as `roster_edit.SHA_RE` written twice (`UNREGISTERED "\\A[0-9a-f]{7,40}\\Z"`). The regex is now `roster_lib.SHA_RE`, and roster_edit reads that one. After the change the lane printed `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`.

There are two merges of main on this branch:
- **`f34f6ec84`** merged `17e621f08` (with #3262 and #3265) into the prototype tip `a37a13bf`. It had one conflict, in `tools/plan/replan.py`, because main had already threaded the cut-over (`legacy`) into `build_plan` and `main()`. The resolution keeps main's `build_plan` signature, its `read_legacy` reader in `main()` and its `round-n-required` mutant anchor. It then adds `dependency_graph(G, legacy)`, the `discharged` set and `summary.groups_discharged` next to main's `post_closure` keys. Before the merge, `git merge-tree --write-tree origin/main HEAD` reported exactly that one file. #3262's `beat_jobs.py` `ROWS` and `RUN` entries were not in conflict. The bottleneck row was added after them later, as a union.
- **`16be6b8b8`** merged `51cd5ec8a`. It was clean, and it touches none of this branch's files.
- **`b87da1699`** merged `daf8b349f`. It was clean, and it also touches none of this branch's files.

## Mutation proof

`python3 dev/audit/harnesses/r10_outside_intake_p2_mutants.py` (new, in-tree) runs every mutant the carry owes. It applies one replacement, runs the mutated file's own `--self-test` (beat_jobs with `--no-mutants`), and restores the file through `mutant_guard`. At this head it printed `RESULT survived=0`:

- `roster_lib.discharged`, one per conjunct. Each is killed by the named roster_lib self-test case:
  - `discharged-any-stage`: "discharged (null): an unmerged group's own work is undone, whatever its carries say".
  - `discharged-no-commit` and `discharged-any-commit`: "discharged (null): carries-open with no recorded merge is not".
  - `discharged-carries-ignored`: "discharged (null): one unmarked carry keeps it owed".
  - `discharged-legacy-ignored`: "discharged: a legacy carry is not owed".
- **replan:** `replan-discharged-arm` (3 FAIL lines) and `replan-legacy-dropped` (2) are killed by the discharged cases.
- **flow_merge_wait:** `wait-after-merge-verdict` (3) and `wait-at-head` (2) are killed.
  - In the first full run, `wait-at-head` SURVIVED: no case read `at_head == False`. A new self-test case, "merge-wait: a verdict on another head is read, not at head", plants a merge verdict on another head 5 min before the merge. It now kills the mutant.
- **train_batches:** `train-done-flag` and `train-skip-first-batch` (2 each) are killed.
- **plan_page:** `page-discharged-label`, `page-done-set` and `page-merged-set` are each killed by "discharged: rendered merged, naming the record step it owes".
- **The beat row:**
  - `beat-memory-dropped` and `beat-rc-clean` are killed, as is `beat-unreadable-dropped`.
  - `beat-missing-key-runs` is killed by "bottleneck: an overlay without train_log is UNREADABLE and runs nothing". Its first form, dropping `train_log` from `need()`, only CRASHED (an IndexError), so it now reads the overlay without `need()` and fails the case.
  - beat_jobs' own `MUTANTS` also carry four kills: `bottleneck_memory_dropped`, `bottleneck_rc_clean`, `bottleneck_unreadable_dropped` and `plan_train_dropped`.
- **mark-carry closing arm:**
  - `mark-close-off` (2) is killed by "mark-carry discharging the last pending carry of a carries-open group writes done" and by "... and holds it carries-open, naming the issue, while it owns an orphaned open issue".
  - `mark-close-any-stage` is killed by "mark-carry's last mark on an in-progress group leaves its stage (null control)".
  - `mark-close-no-hold` is killed by the held case.
- **bottleneck_check's own 10 rule mutants:** every one is killed (`ok: bottleneck_check self-test`).
- **The state_docs `--train-log` hand-on.** Removing `"--train-log", str(train)` from the self-test's argv fails "plan page: --train-log reaches plan_page.py: the page's train skips name its batch", and restoring it passes.

## Null control

- Harness M0, nothing replaced, runs all six self-tests and prints `RESULT mutant=M0 rc=0 fails=0 verdict=null`. Every kill above therefore belongs to its mutant.
- `r10_plan_page_mutants.py M0` printed `verdict=null` at main `17e621f08` and `verdict=SURVIVED` (1 FAIL, the state_docs check above) at `f34f6ec84`. It prints `verdict=null` at this head.
- For the replan figures, the base arm is main's own `replan.py` (`git archive origin/main`) on the same roster and the same `--start`. Its `groups_discharged` key is absent, and it schedules every group.
- The mark-carry arm has two null controls. A last mark on an `in-progress` group leaves its stage. A mark that leaves one carry pending keeps `carries-open`.

## Figures

- **Replan, both arms.** Command: `python3 -I <tree>/tools/plan/replan.py --repo . --roster-ref origin/handoff/audit-r10-roster --start 2026-11-08T20:20:00Z --slots 20 --seats 20 --out plan-<arm>.json`. `<tree>` is `git archive origin/main` (the base, at main `17e621f08`) or `git archive` of this branch at `78d409286`. The roster was `origin/handoff/audit-r10-roster` at `fcc9a1933aa1`, read 2026-11-08T20:20Z. The figures are read from `summary` and `groups[*].discharged`:
  - base: closure 2026-11-15T07:03:00Z, 49 batches, 6075.0 CI minutes, 324 done / 71 open.
  - head: closure 2026-11-15T07:03:00Z, 48 batches, 5962.5 CI minutes, 327 done / 68 open, `groups_discharged` 3.
  - The 3 groups are R10-CI-GRADER-BATCH-STUDY, R10-FRICTION-CI-RED and R10-FRICTION-OTHER-FAMILY, each `carries-open` with a recorded commit and no carry. Their wired issues are none, #3156, and #3283 #3313 #3314 respectively; the first owes only `set-stage done`.
  - The critical path is identical in both arms: R10-GENERIC-HEAT-CURVE, R10-GENERIC-HEAT-CURVE-PERSISTENT, R10-ARBITER-OFF-RESTORE, R10-ARCH-DOCS, R10-CLOSEOUT-CLEANUP. So the closure date does not move on this roster.
  - The figures are a function of the roster tip and `--start`. On another roster, re-run the same command rather than carry them.
- `python3 dev/audit/harnesses/r10_outside_intake_p2_mutants.py` at `3db23178b`: 21 mutants `verdict=killed` (`grep -c`), M0 `verdict=null`, `RESULT survived=0`, rc 0.
- Self-tests at this head (`python3 -I <file> --self-test`):
  - `roster_lib.py`: `roster_lib self-test: 72 checks, 0 failed`.
  - `roster_edit.py`: `roster_edit self-test: 246 checks, 0 failed`.
  - `replan.py`: `self-test: 0 failed`.
  - `merge_throughput.py`: `ok: merge_throughput.py self-test`.
  - `plan_page.py`: `plan_page self-test: 75 checks, 0 failed`.
  - `bottleneck_check.py`: `ok: bottleneck_check self-test`.
  - `beat_jobs.py`: `beat_jobs self-test: 185 checks, 0 failed`.
  - `state_docs.py`: `state_docs self-test: all checks passed`.
  - `beatd.py`: `beatd self-test: 119 checks, 0 failed`.
  - `hooks_setup.py`: `hooks_setup self-test: 39 checks, 0 failed`.
  - `sweep_render.py`: `sweep_render self-test: 34 checks, 0 failed`.
- `python3 tools/audit/seat/selftest_wiring.py --check`: `125 self-testing, 125 wired, 0 unwired`. Before the governance.yml step it printed `UNWIRED tools/audit/seat/bottleneck_check.py`.
- **Gate scope.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` at `78d409286`. The two scripts are `tests/entities.py` and `tests/harness_headers.py`.
- **Scoped scripts**, with `PYTHONPATH=tests/hastub`, at `78d409286`:
  - `tests/entities.py`: `ALL 2668 ENTITY CHECKS PASSED`.
  - `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - The `run_always` lines: `tests/env_drift.py --claims-only` printed `claims hygiene: 17e621f08c4feec724478573741fbd8b596ceaba ok`, and `tests/closure.py selftest` printed `ALL 118 closure shrink pins PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No `*_budgets.json` is in the three-dot diff.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- `VERSION`, `RELEASE_NOTES.md`, the manifest and both claim files are untouched by the three-dot diff. No golden was run, because the diff touches none.
- Toolchain: `bash tools/audit/seat/cloud-setup.sh --check` printed `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` at `b87da1699`: `PRE-PR: b87da16993f1dff1bbbf7c8fae6de93bbcfcb515 0000000000000000000000000000000 rc=0`.

## Red checks

none have run at this head. Before the handoff, `ci_predict.py` (prepr step 6d) predicted 7 reds at `16be6b8b8`, and each was repaired here:
- the H2 anchor in `r10_roster_ops_mutants.py`;
- the unregistered duplicate grammar in the agreement lane;
- the two INERT READS;
- the carry audit's unrouted Forward-carry item.

`tests/closures.json` was not re-derived here (`PREPR_SKIP_CLOSURES=1`). `plan_page.py` now imports `merge_throughput.py` and `bottleneck_check.py`, so an UNDER-SCOPED `closures` red is the `closures-autofix` job's to repair on the pull request (`ci-autofix.md`). Cheaper detector: none is owed. `ci_predict.py` is that detector, and it ran before the handoff.

## Unpinned sites

none: prepr's unpinned-sites step reported `the diff adds no unpinned mutation site`.

## Forward-carry

none

## Friction

- brief: stale: the roster carry says `r10_plan_page_mutants.py` M0 "fails on main as well as on this tip"; at main `17e621f08` M0 printed `verdict=null`, and only the tip failed (the Flow section's UNAVAILABLE cells), repaired here. Carry: dismissed: repaired in this pull request, and the carry is consumed by this landing
