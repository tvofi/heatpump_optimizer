R10-OUTSIDE-INTAKE part 2: the plan-page closure rule, the Flow section and the bottleneck alert. This is the group's part 1 (#3262) follow-on, built from the prototype at `handoff-wip/r10-outside-intake-p2` (`a37a13bf`) and continued from it, fast-forward only.

The owner, verbatim (tvofi 2026-11-07): "1: groups with all it's carries absorbed by another group should be considered closed, if that is not unsound for some reason. 2: Add flow board metrics in the plan HTML and a mechanism to alert you [the orchestrator] on bottlenecks and enable you to decide whether to act on it. Build it locally first and have the public plan page group land it on main."

**A workflow and the sweep template change: this needs tvofi's approving review** (`.github/workflows/governance.yml` gains one self-test step, gated as `bottleneck-alert` under `tools/ci/selftest_scope.py`'s rule, with its measured row in `tools/ci/selftest_closures.json`; `tools/audit/seat/sweep_template.md` gains the `train_log` placeholder and one sentence on what a `BOTTLENECK:` line asks of the sweep).

**Carry 1** (roster `R10-OUTSIDE-INTAKE`, part 2) is discharged by this pull request in full:
- the closure rule and the record-lag writer (items 1-2 below);
- the flow metrics, the alert and the beat row with `--train-log` passed (items 3-5);
- every mutant it owed (under Mutation proof);
- the disposition of `r10_plan_page_mutants.py` M0, which is repaired (item 6).

**Carry 2** (roster `R10-OUTSIDE-INTAKE`, the plan-page note under the Projected open issues chart: pluralise the count, drop the zero clause) is **not** discharged by this pull request. It reached the roster from the 2026-11-08 plan-page read, after this branch was cut, and this round is a merge resolution with main, which builds no carry. It stays unmarked on the roster, so the group stays `carries-open` and the carry stays owed by its next dispatch.

**Carry 3** (roster `R10-OUTSIDE-INTAKE`, triage batch 138 `PLAN-PAGE-NONE-LEAK`: `wave None` in `data-wave` and the bar tooltip, and the sort key's list repr) and **Carry 4** (triage batch 139, its extension: the status strip's part-merged count from a second predicate, and a raw markdown heading in a group description) are **not** discharged by this pull request, for the same reason as Carry 2: both reached the roster after this branch was cut, and this round is a merge resolution with main: its one `tools/audit/seat/plan_page.py` production line is `build_rows`' blocked list, and its self-test case is the stamp axis, neither in the render seam those carries name. Both stay unmarked on the roster and owed by the group's next dispatch, beside Carry 2 in the same render seam.

What lands:

1. **Closure rule (proposal 1).** `roster_lib.discharged`: a group at `carries-open`, with a merge sha in `resume.commit`, that owes no carry (every carry is marked implemented, moved or dismissed, or is legacy at the cut-over). Any other stage is never discharged, because the group's own brief is undone. `replan.dependency_graph` counts a discharged group done, so it takes no slot, pays no batch and clears its after-edges. `plan.json` gains a per-group `discharged` flag and `summary.groups_discharged`. The roster stage is not rewritten. `plan_page.py` renders a discharged group as merged, labelled `every carry discharged; record owed: close or re-own #..., then set-stage done`.
2. **The record lag, closed at its writer.** `roster_edit.py mark-carry`: when a mark discharges the last pending carry of a `carries-open` group, it applies set-stage done's own closing rule (`roster_lib.closing_stage`, then `hold_done`'s `carry_audit.orphaned` test). It writes `done`, or keeps the group `carries-open`, prints `HELD` and names each open issue that holds it (`close_discharged`). No beat writes `set-stage done`, because the orphan rule would hold it anyway.
3. **Flow metrics (proposal 2).** These are computed in `tools/audit/merge_throughput.py` and imported by the page and the alert, never copied. They are `flow_merge_wait`, `train_batches`/`read_train_batches` and `bottleneck_metrics`, which composes them with `flow_closed`, `flow_verdicts`, `flow_lead` and `pr_cap.wip_groups`. `plan_page.py` draws a Flow section after the issue chart, and takes `--train-log` and `--no-flow`. The tip also carries the prototype's mobile layout and the issue projection read through `fixes`.
4. **The alert.** The new `tools/audit/seat/bottleneck_check.py` prints `BOTTLENECK: <metric> <value> vs <threshold> -- <suggested action>` per breach and nothing on success. A source it cannot read gives `BOTTLENECK-UNREADABLE: <metric> -- <why>`. It suggests, and the orchestrator decides. The thresholds and minimum samples are the owner's (`THRESHOLDS`). Throughput keeps `flow_closed`, which counts roster closes rather than merges. The instrument doc says so, and says that a hand record batch reads as a burst. Its self-test runs in `governance / instrument-self-tests` as step `bottleneck-alert`, selected on a pull request by its measured read set like every other gated step.
5. **The beat.** `beat_jobs.py` gains a `bottleneck` row after #3262's `outside-intake`, in `ROWS`, `RUN` and `beatd.jobs.json`, every 1800 s. It runs with the beat checkout, the overlay's new `train_log` key, the `plan_slots` cap and `--memory state/bottleneck.json`, so a held breach is new once per trip. A missing key or a failed check is UNREADABLE. `plan-beat` hands `train_log` to `state_docs.py`, whose new `--train-log` passes on to `plan_page.py`, so the page's skip-share and train-skips table read the live log.
6. **r10_plan_page_mutants.py M0: repaired.** At main `17e621f08`, M0 printed `verdict=null`. On the prototype it failed, because the state_docs self-test check "a fresh plan draws PLAN.html in the plan table's commit" required `"UNAVAILABLE" not in good`, and the Flow section's UNAVAILABLE metric cells are in a healthy page. The check now keys on `PLAN UNAVAILABLE`, the refusal page's own heading, as `draw_plan_page`'s crash guard already does. M0 prints `verdict=null` at this head. The design choice (`fixer.md` step 11): a drawn page may carry an UNAVAILABLE metric, and only the refusal page is the UNAVAILABLE page.

Alternatives, and why each lost (`fixer.md` step 17):
- **Rewriting the roster stage to `done` from the plan, or from a beat.** `roster_sync.hold_open` and the done hold keep a group `carries-open` while it owns an open issue nothing else owns. A writer that bypassed that would orphan the issue. The plan only views the group as closed, and the roster's one closing writer (`_closing` plus `hold_done`) is reused by mark-carry.
- **Marks-aware pricing of partly discharged groups** (open carries = the min of the measured count and the unmarked count). The roster carry measured it at 0 h of closure movement, so it is not built.
- **Copying the flow computations into the page or the alert.** That would create two owners of one metric, so both import `merge_throughput`.
- **Throughput from group merges.** It would add a second throughput definition beside the flow board's, so it is deferred and documented. The roster's write time is the flow board's rule.
- **The self-test step on `selftest_scope.UNGATED`** instead of gated. `UNGATED` holds the job's own machinery (`scope`, `strace`, `launch`, `drift`, `unread`: they choose, trace, start, audit); the bottleneck self-test is an ordinary instrument self-test, and listing it there would run it on every pull request for no reason the rule recognises.

## Head

`f95b593a5f2e544cd7e297f3ca72cfc887ec6576` is `bb84b1bd27dc80118ab088fd2d2b8181e09cea71` plus a merge of origin/main `2f6d699e504d` (read 2026-11-09T17:16Z) and five commits. **Resolution delta for the reviewer** (judge this delta alone, `fix-review.md` step 12):

- `855003fbf`, the merge. Its one textual conflict was `tools/plan/replan.py` `build_plan`, against #3326 R10-FLY-REPLAN-DEFECTS. The union: `dependency_graph(G, legacy)` keeps this PR's discharged-as-done read and takes main's `roster_lib.gates(G[a])` edge release; `build_plan` keeps `discharged` and takes main's deferred hold, computed as `roster_lib.held_behind_deferred(live)` over `live`, the roster less its discharged groups, so a discharged group is neither held nor holds, as `dependency_graph` reads it. Main's mutant rows `edge-releases-ruled` and `deferred-holds-dependent` follow the new signature and view. New: selftest pair 3d (`discharged behind deferred: closed and not held; its dependent released`, and its null, one unmarked carry keeps both held) and mutant row `discharged-not-held` (`held_behind_deferred(live)` -> `(G)`). The selftest helper `held()` is renamed `carrying()`; main's 3c loop rebinds `held` in the same function.
- `7f505becb`, the semantic conflict git did not report. `tools/audit/seat/plan_page.py` `build_rows` auto-merged main's blocked list `if a in G and roster_lib.gates(G[a])`, which reads a discharged (`carries-open`) predecessor as gating, so plan_page's case `discharged: rendered merged, naming the record step it owes` failed and the group harness's M0 printed `verdict=SURVIVED`. The line is now `if a in G and a not in discharged and roster_lib.gates(G[a])`. `r10_plan_page_mutants.py` rows `blocked-by-less-done` and `defect-2-scratch-graph` anchored main's pre-#3326 line and are re-anchored on this one.
- `f86004e5c`: harness row `page-done-set` printed `SURVIVED` after the merge, because the discharged edge release no longer reads `done`; `done`'s `| discharged` now feeds only a row's wave/start/finish, which replan already nulls for a discharged group. The row is renamed `page-discharged-edge` and deletes the release in the blocked list.
- `9dca46ba9` and `c0ad3ad51`: `r10_plan_page_mutants.py` aborted at row `stamp-on-axis` (`occurs 0 times`) at `bb84b1bd` and on main alike, since `857586f29` wrapped the axis-end expression, so none of the 13 rows after it ran. The row is re-anchored on the wrapped line; it then printed `SURVIVED`, and plan_page gains the case `every planned stamp is drawn on the axis, the round-close one after closure included`, which kills it.

- `f95b593a5`: `prepr.sh` refused the claims register, `claims_true=122 (header 123) claims_false=1`. origin/main itself grades D6 claim C112 false (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` on `git archive origin/main`: `FALSE C112 ... every translation file carries exactly the keys strings.json declares`, `claims_false=1`): `strings.json` gained `flow_min_lift_k` and `flow_heat_c` (label and description) and the `space_setpoint_unit` option `return` after #3331 merged `translations/de.json`, which carries none of the five. They are added in German, terms taken from `de.json`'s own (Steuerung der Pumpenfunktion, Steuern, Zulauf, Sollwert); no other line of the file changes (a JSON round-trip of the base file is byte-identical).

The merge base is now `2f6d699e504d6dc0bb6040d99c21c5b015a290e4`.

Previous round: `bb84b1bd27dc80118ab088fd2d2b8181e09cea71` is `9f4a1a41078ab70510afe7e2413ac603e0ffdd56` plus one commit, the **selftest_scope fix** (verdict `verdict/3350` `3fe414f2`, `blocked 9f4a1a41 resolution-ungated-step`): the governance.yml step `Show the bottleneck alert tripping each rule once and silent on its null control` gains `id: bottleneck-alert` and `if: steps.scope.outputs.bottleneck-alert == 'true'`, and `tools/ci/selftest_closures.json` gains its `bottleneck-alert` row, recorded by `python3 -I tools/ci/selftest_scope.py record --step bottleneck-alert` (Linux, strace), the re-record that file's docstring and #201 comment 6707834331 name. The row was measured, not written: `files` names `tools/audit/seat/bottleneck_check.py`, `index` and `objects` are false. No other line changed; the rule in `selftest_scope.py` is untouched. **No merge**: `git merge-tree --write-tree origin/main HEAD` at `bb84b1bd` against origin/main `631ac4df34c9` (read 2026-11-09T13:40Z) exited 0, no conflict, so main was not merged in (brief item 2). The merge base stays `f365ce757ded1e64a9ec40102495b7c051055f38`.

`9f4a1a41078ab70510afe7e2413ac603e0ffdd56` merges main `f365ce7` into the previous head: an automatic merge by the orchestrator, no textual resolution; main's selftest_scope rule read the branch's unchanged step as ungated, which this head repairs.

`ab236e012dedd0c24039a4b530dcc83ebd20d3b3` merges the authored code head `50d4c7e0e2c64de8bf9523fe1b8723c88669d899`.

`50d4c7e0e2c64de8bf9523fe1b8723c88669d899`: review round 3350r4's head `f3e7fcc32b6100699aaf41213df06353440ccfbb` (tree identical to `db13cc6e69c92c3e5b8dd38ba1b4e1659c4bf640`) plus two commits repairing its follow-up (a self-test case and the harness row for its mutant). Figures marked "this round" were taken at `bb84b1bd`; the rest are earlier rounds' and name their commit.

Earlier rounds' repairs, kept for the figures that name them:
- **bottleneck_check trip memory keyed by kind and metric** (at `db13cc6e`). `remembered` keyed its memory by `metric_of(line)`, the second word, shared by `BOTTLENECK-UNREADABLE: yield -- ...` and `BOTTLENECK: yield 0.40 ...`, so a real breach on the beat after an UNREADABLE one re-printed the stale UNREADABLE line. The key is now `state_of(line)`, the line's first two words. An old memory file keyed by metric alone misses every key once and prints afresh, the recovery path. Alternative that lost: storing `(kind, line)` per metric and comparing kinds; it keeps the metric as the key and adds a second field for the same distinction the key already carries.
- **roster_edit mark-carry's read of the cut-over pinned.** A self-test case: on the R9-L fixture (one legacy carry at the cut-over, one post-cut-over carry, `carries-open`), marking the post-cut-over carry writes `done`. Dropping `"mark-carry"` from `make_edit`'s `("set-stage", "set-resume", "mark-carry")` tuple fails it.

Earlier heads, for the figures that name them: `b99248e2` (bot re-record), `f10cb23fb` and `2fb9b2467` (merges of origin/main, no conflict), `9106db479` (merge of `2fb9b2467`, reviewed by 3350r3).

## Mutation proof

This round (at `c0ad3ad5`), each replacement applied to the committed tree and restored:
- `discharged-not-held` (`held = roster_lib.held_behind_deferred(live)` -> `(G)`), by hand: `python3 tools/plan/replan.py --self-test` printed `FAIL discharged behind deferred: closed and not held; its dependent released` and `self-test: 4 failed` (the other three are the copy's own null control and the two mutant rows whose anchor the hand edit removed); restored, `self-test: 0 failed`. The in-file row prints `ok   self-test fails when discharged-not-held is deleted`.
- `page-discharged-edge`: `python3 -I dev/audit/harnesses/r10_outside_intake_p2_mutants.py M0 page-discharged-edge`: `verdict=killed`, its one FAIL line `discharged: rendered merged, naming the record step it owes`; M0 `verdict=null`.
- `stamp-on-axis`: `python3 -I dev/audit/harnesses/r10_plan_page_mutants.py M0 stamp-on-axis`: `verdict=killed`, its one FAIL line `every planned stamp is drawn on the axis, the round-close one after closure included`; before that case was added (at `9dca46ba9`) the same row printed `verdict=SURVIVED`.

Round 6 (at `bb84b1bd`): **the wiring reverted.** With `.github/workflows/governance.yml` restored to `9f4a1a41`'s step (no `id:`, no `if:`) and the recorded table row kept, `python3 -I tools/ci/selftest_scope.py --self-test` prints `FAIL the live job parses (115 steps) and its gating is consistent` and `selftest_scope self-test: 90 checks, 1 failed`, rc 1; restored, `ok   the live job parses (115 steps) and its gating is consistent`, `90 checks, 0 failed`, rc 0. **The table row reverted.** With `tools/ci/selftest_closures.json` restored to `9f4a1a41`'s and the wiring kept, `python3 -I tools/ci/selftest_scope.py select --change M:tools/audit/seat/bottleneck_check.py` prints `MODE: FULL -- every step runs (the table is stale: its steps differ from the workflow's: missing ['bottleneck-alert'], extra [])`; restored, `MODE: SCOPED -- 20 step(s) run`, naming `run bottleneck-alert`.

Round 5 (at `50d4c7e0`): **`state_of` -> kind only.** New case in bottleneck_check's `self_test`: `memory: two metrics tripped together each print their own line` (throughput and wip tripped in one beat, `--memory` form; asserts two lines, each its own). `python3 -I dev/audit/harnesses/r10_outside_intake_p2_mutants.py M0 state-of-kind-only` (harness row replacing `state_of`'s `return " ".join(line.split()[:2])` with `return line.split()[0]`): `RESULT mutant=M0 rc=0 fails=0 verdict=null`; `RESULT mutant=state-of-kind-only rc=1 fails=4 verdict=killed`, whose first FAIL line is the new behaviour case; `RESULT survived=0`. bottleneck_check's in-file `MEMORY_MUTANTS` gains `memory-key-kind` (same replacement); the self-test prints it `killed`.

At `db13cc6e`:
- **Failing test first.** With the three new memory cases added and `remembered` unchanged, `python3 -I tools/audit/seat/bottleneck_check.py --self-test` printed `FAIL memory: a breach after UNREADABLE for one metric prints the breach: ['BOTTLENECK-UNREADABLE: throughput -- no source']` and `FAILED: bottleneck_check self-test`; with the fix, `ok: bottleneck_check self-test`.
- **Key reverted.** bottleneck_check's in-file `MEMORY_MUTANTS` entry `memory-key-metric` replaces `state_of`'s `return " ".join(line.split()[:2])` with `return line.split()[1]` (the pre-fix key); the self-test prints `ok   mutant memory-key-metric killed`. `run_mutants` applies each mutant to its named function (`judge` or `state_of`).
- **mark-carry legacy read.** `python3 -I dev/audit/harnesses/r10_outside_intake_p2_mutants.py M0 mark-close-off mark-legacy-dropped`: `RESULT mutant=mark-legacy-dropped rc=1 fails=1 verdict=killed`, its one FAIL line `mark-carry whose only unmarked carry left is legacy writes done`; `mark-close-off` also fails that case (3 FAIL lines); M0 `verdict=null`; `RESULT survived=0`.

Earlier rounds:

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

- This round: the 3d pair's null (`discharged behind deferred (null)`, one unmarked carry) passes at the head and reads the group and its dependent held, so the case separates discharged from open, not every carries-open group. Both harnesses' M0 print `verdict=null` at `c0ad3ad5`. At `bb84b1bd` (detached worktree, the same commands) `r10_outside_intake_p2_mutants.py` printed `RESULT survived=0` and `r10_plan_page_mutants.py M0 blocked-by-less-done defect-2-scratch-graph` printed each `verdict=null`/`killed`; the full plan-page harness aborted at `stamp-on-axis` there, as on main.
- This round: the failing arm of the wiring proof is `9f4a1a41`'s own tree, where the verdict measured the same `FAIL` line, and main `f365ce757`, where the verdict measured `ok ... (114 steps)`, 90 checks and 0 failed: the self-test separates gated from ungated, not a 115th step from 114. The selection proof's null control is the reverted table, which reads stale; the selection is scoped only with the row present.
- At `db13cc6e`: "memory: UNREADABLE then UNREADABLE stays its first line (null control)" passes both before and after the fix (a second UNREADABLE beat with a different reason re-prints the first line), so the fix splits only kinds, not every beat. "memory: a still-tripped metric re-prints its first line verbatim" is unchanged and passes. The mark-carry case's null control is the existing "a carry after the cut-over is pending beside a legacy one" on the same group with that carry unmarked, which reads `carries-open`.
- Harness M0, nothing replaced, runs all six self-tests and prints `RESULT mutant=M0 rc=0 fails=0 verdict=null` (this round, at `bb84b1bd`), so every kill above belongs to its mutant.
- `r10_plan_page_mutants.py M0` printed `verdict=null` at main `17e621f08` and `verdict=SURVIVED` (1 FAIL, the state_docs check above) at `f34f6ec84`; `verdict=null` at `b87da1699`.
- For the replan figures, the base arm is main's own `replan.py` (`git archive origin/main`) on the same roster and the same `--start`. Its `groups_discharged` key is absent, and it schedules every group.
- The mark-carry arm has two null controls: a last mark on an `in-progress` group leaves its stage; a mark that leaves one carry pending keeps `carries-open`.

## Figures

This round, at `f95b593a5` (the harness, self-test and ratchet figures were taken at `c0ad3ad5`, whose tree differs from `f95b593a5` only in `translations/de.json`, which none of them reads; merge base `2f6d699e5`, origin/main read 2026-11-09T17:16Z):
- `git merge-tree --write-tree origin/main bb84b1bd`: `CONFLICT (content): Merge conflict in tools/plan/replan.py`, the only conflict.
- `python3 tools/plan/replan.py --self-test`: `self-test: 0 failed`, rc 0 (at `bb84b1bd`: `self-test: 0 failed`, rc 0).
- `python3 -I dev/audit/harnesses/r10_outside_intake_p2_mutants.py`: M0 `verdict=null`, every other row `verdict=killed`, `RESULT survived=0`, rc 0. At `bb84b1bd`: the same. At the merge commit `855003fbf` before `7f505becb`: `RESULT mutant=M0 rc=1 fails=1 verdict=SURVIVED`, `RESULT survived=1`.
- `python3 -I dev/audit/harnesses/r10_plan_page_mutants.py`: M0 `verdict=null`, every other row `verdict=killed`, `RESULT survived=0`, rc 0. At `bb84b1bd`: rc 2, `abort: stamp-on-axis: ... occurs 0 times`.
- `python3 -I tools/audit/seat/plan_page.py --self-test`: `plan_page self-test: 76 checks, 0 failed` (75 at `bb84b1bd`, plus the axis case).
- `python3 -I tools/audit/seat/roster_lib.py --self-test`: `81 checks, 0 failed`; `python3 -I tools/ci/selftest_scope.py --self-test`: `90 checks, 0 failed`; `python3 -I tools/audit/seat/bottleneck_check.py --self-test`: `ok: bottleneck_check self-test`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: FULL`, reason `tools/ci/selftest_closures.json changes the gate itself`; left to CI (`fixer.md` step 5).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- At `f95b593a5`, `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` on a copy of the tracked tree: `RESULT claims_false=0 claims` (origin/main: `claims_false=1`, C112). `PYTHONPATH=tests/hastub python3 tests/<script>.py` for the scripts that read `translations/`: `config_flow_steps` `ALL 549 checks PASSED`, `deployment_shape` `ALL DEPLOYMENT SHAPE CHECKS PASSED`, `doc_claims` `ALL 297 checks PASSED`; `entities` did not finish inside 220 s locally and is left to CI's FULL run.

Round 6, at `bb84b1bd` (each the command named, run in this worktree, merge base `f365ce757`):
- `python3 -I tools/ci/selftest_scope.py --self-test`: `selftest_scope self-test: 90 checks, 0 failed`, rc 0; at `9f4a1a41`, the same command: `90 checks, 1 failed`, rc 1 (`FAIL the live job parses (115 steps) and its gating is consistent`).
- `python3 -I tools/ci/selftest_scope.py select --base origin/main`: `MODE: FULL -- every step runs (a gate file changed: ['.github/workflows/governance.yml'])`, by GATE_FILES' rule, so this pull request's own self-test job runs every step, `bottleneck-alert` among them.
- `python3 -I tools/ci/selftest_scope.py record --step bottleneck-alert`: `selftest_scope: recorded 1 step(s) into .../tools/ci/selftest_closures.json; 0 failed []`.
- `python3 -I tools/audit/seat/bottleneck_check.py --self-test`: `ok: bottleneck_check self-test`.
- `python3 -I dev/audit/harnesses/r10_outside_intake_p2_mutants.py M0`: `RESULT mutant=M0 rc=0 fails=0 verdict=null`, `RESULT survived=0`.
- `python3 tools/audit/seat/selftest_wiring.py --check`: `selftest_wiring: 0 index gap(s)`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: FULL -- every test script runs, nothing is scoped out.`, reason `tools/ci/selftest_closures.json changes the gate itself, so every closure is suspect`. Under `fixer.md` step 5 a FULL mode is a diff the gate cannot scope, left to CI rather than reproduced.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- `bash tools/audit/seat/cloud-setup.sh --check`: `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`.
- `VERSION`, `RELEASE_NOTES.md`, the manifest, both claim files and every `*_budgets.json` are untouched by the three-dot diff. No golden was run, because the diff touches none.

At `db13cc6e`:
- `python3 -I dev/audit/harnesses/r10_outside_intake_p2_mutants.py` (every mutant, including `mark-legacy-dropped`): M0 `verdict=null`, every other `RESULT mutant=` line `verdict=killed`, `RESULT survived=0`.
- `python3 -I tools/audit/seat/bottleneck_check.py --self-test`: `ok: bottleneck_check self-test`; its 10 rule mutants and `memory-key-metric` each print `killed`.
- `python3 -I tools/audit/seat/roster_edit.py --self-test`: `roster_edit self-test: 261 checks, 0 failed` (260 at `9106db479`, plus the one new case).
- Gate scope then: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`; `scope.run` named `tests/entities.py` and `tests/harness_headers.py`. With `PYTHONPATH=tests/hastub`: `ALL 2668 ENTITY CHECKS PASSED`, `ALL 112 HARNESS HEADER CHECKS PASSED`. `run_always`: `claims hygiene: origin/main ok`, `ALL 118 closure shrink pins PASSED`.

Earlier rounds:

- **Replan, both arms** (taken at `78d409286`). Command: `python3 -I <tree>/tools/plan/replan.py --repo . --roster-ref origin/handoff/audit-r10-roster --start 2026-11-08T20:20:00Z --slots 20 --seats 20 --out plan-<arm>.json`. `<tree>` is `git archive origin/main` (the base, at main `17e621f08`) or `git archive` of this branch at `78d409286`. The roster was `origin/handoff/audit-r10-roster` at `fcc9a1933aa1`, read 2026-11-08T20:20Z. Read from `summary` and `groups[*].discharged`:
  - base: closure 2026-11-15T07:03:00Z, 49 batches, 6075.0 CI minutes, 324 done / 71 open.
  - head: closure 2026-11-15T07:03:00Z, 48 batches, 5962.5 CI minutes, 327 done / 68 open, `groups_discharged` 3.
  - The 3 groups are R10-CI-GRADER-BATCH-STUDY, R10-FRICTION-CI-RED and R10-FRICTION-OTHER-FAMILY, each `carries-open` with a recorded commit and no carry. Their wired issues are none, #3156, and #3283 #3313 #3314 respectively; the first owes only `set-stage done`.
  - The critical path is identical in both arms: R10-GENERIC-HEAT-CURVE, R10-GENERIC-HEAT-CURVE-PERSISTENT, R10-ARBITER-OFF-RESTORE, R10-ARCH-DOCS, R10-CLOSEOUT-CLEANUP, so the closure date does not move on this roster.
  - The figures are a function of the roster tip and `--start`; on another roster, re-run the same command rather than carry them.
- Self-tests at `f10cb23fb` (`python3 -I <file> --self-test`), the files main's merge reaches:
  - `tools/audit/seat/roster_edit.py`: `roster_edit self-test: 260 checks, 0 failed`.
  - `tools/audit/seat/roster_lib.py`: `roster_lib self-test: 72 checks, 0 failed`.
  - `tools/audit/seat/r10_roster_ops_mutants.py`: `r10_roster_ops_mutants self-test: 321 checks, 0 failed`.
- Self-tests at `b87da1699`: `replan.py` `self-test: 0 failed`; `merge_throughput.py` `ok: merge_throughput.py self-test`; `plan_page.py` `plan_page self-test: 75 checks, 0 failed`; `beat_jobs.py` `beat_jobs self-test: 185 checks, 0 failed`; `state_docs.py` `state_docs self-test: all checks passed`; `beatd.py` `beatd self-test: 119 checks, 0 failed`; `hooks_setup.py` `hooks_setup self-test: 39 checks, 0 failed`; `sweep_render.py` `sweep_render self-test: 34 checks, 0 failed`.
- `python3 tools/audit/seat/selftest_wiring.py --check` (at `b87da1699`): `125 self-testing, 125 wired, 0 unwired`. Before the governance.yml step it printed `UNWIRED tools/audit/seat/bottleneck_check.py`.

## Red checks

Only the reds in the set `python3 tools/audit/seat/merge_train.py owed-reds --repo tvofi/heatpump_optimizer` prints are answered here (the owner's ruling of 2026-11-09).

At `9f4a1a41`: no check in that set went red (every one reads `success` or `skipped` on the PR's check-runs listing). The one red there, `governance / instrument-self-tests` (job 129152227797), is outside the set; it is the failure this head repairs (`## Head`).

At `9106db479`: `gate` job 128917441489 (run 42539681502) and `gate` job 128920205614 (run 42540557389) concluded `failure` as deferrals (`FAIL run(s) [...] at this head are still being judged; their gate decides`), while the code run 42539680047 they deferred to published `gate` `success`. The orchestrator re-ran both at 03:59Z. They are deferrals, not defects. Cheaper detector: none exists; a deferral is the gate waiting on its own code run, and nothing cheaper than that run judges the head.

At `b99248e2`, each red and cancelled check in the set by name; none is a failure the branch caused:
- `gate` (run 42529990775): `cancelled`. Its run was superseded at the same head by run 42529995793 (`cancel-superseded`, the `pull_request` attempt `hpo-runs` released). Cheaper detector: none exists; a cancellation is not a defect.
- `tests / coverage-ratchet`, `tests / ci-ratchet` (run 42529990775): `cancelled`, the same supersession. Cheaper detector: none exists, as above.
- `tests / fast (3.14)`, `tests / coverage`, `tests / closures`, `codeql / Analyze (python)` (run 42529990775): `cancelled` by the same supersession; in run 42529995793 at the same head `tests / fast (3.14)` completed `success`, and the other three were still running when read (2026-11-08T23:16Z). Cheaper detector: none exists.
- `tests / closures` was red earlier on this PR as UNDER-SCOPED (`plan_page.py` imports `merge_throughput.py` and `bottleneck_check.py`), repaired by the `closures-autofix` bot commit `b99248e2` (`ci-autofix.md`). Cheaper detector: `ci_predict.py` (prepr step 6d) is it, and it ran before the handoff; `PREPR_SKIP_CLOSURES=1` leaves the re-derivation to the bot by design.

## Unpinned sites

none: prepr's unpinned-sites step reported `the diff adds no unpinned mutation site`.

## Forward-carry

none

## Friction

- brief: stale: the repair brief reads four `cancelled` rows of a superseded `workflow_dispatch` run as "real reds, not gate deferrals"; every one is `conclusion: cancelled` and the same head's `pull_request` run was live. Carry: dismissed: no stage's method changes; a cancelled row is read by its conclusion field, which this body records
- brief: stale: the roster carry says `r10_plan_page_mutants.py` M0 "fails on main as well as on this tip"; at main `17e621f08` M0 printed `verdict=null`, and only the tip failed (the Flow section's UNAVAILABLE cells), repaired here. Carry: dismissed: repaired in this pull request, and the carry is consumed by this landing
