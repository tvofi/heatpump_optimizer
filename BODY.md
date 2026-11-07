R10-FLOW-TOOLKIT-MODEL: plan-model correctness in tools/plan/replan.py, plus the tracked Gantt-drift instrument (carry 12). Measures the roster/plan semantics only; no production code.

This repair round lands carry 15 (0-based; "From the s12 slip study (2026-11-07)"), on top of the merge-only conflict seat's head d84006e66001d42c744448949159f6473adedcd6, fast-forward. `git merge-tree --write-tree origin/main HEAD` reported no conflict at the start, so no merge was made.

Carry 15: `held_open` counted `len(group carry)` and `group_hours`' absorbed-carry term counted `len(group carry)`, so a carry `roster_edit.py mark-carry` had discharged (implemented, moved, dismissed) still priced as open work. Both now count `roster_lib.pending_carries` (unmarked and not legacy):

- `held_open(group, durations, pending)`: an unmeasured group counts its pending carries; a measured one (`held_open_carries`) counts `min(open at measurement, pending carries among those then held)` plus the pending carries appended since. With no carry marked this is exactly the old figure.
- `group_hours(..., legacy=None)`: computes `pending` once, prices the absorbed-carry term on `len(pending)`, and the duration basis ends `, N marked carries left out` whenever any carry was left out.
- `build_plan(..., legacy=None)` threads the cut-over through; `main` reads it with `roster_lib.read_legacy(repo, ROSTERS_DIR/<roster basename>)`, so a `--roster-file` copy named `wave-r10-groups.json` keeps its round's cut-over (`roster_lib.CARRY_CUTOVER`). A cut-over the clone cannot read refuses as a `PlanError`, never "no legacy".

`replan --measure-sizes` was not used (the verifier found it does not deliver the saving).

Earlier rounds (unchanged by this repair, kept from the previous body): carries 0, 2, 3, 8, 9, 10, 11 and 12 built; 1 and 7 moved to R10-BODY-CONTRACT; 4, 5 and 6 dismissed as duplicates; review items 1-5 and round-5 items 1-2 repaired, item 7 dismissed with its reason; the merge resolutions in `is_done`/`plan_page.py` are as described on the earlier heads.

## Head

55b86a71ea5752e1af9f6491a94798629df236b2, a fast-forward of d84006e66001d42c744448949159f6473adedcd6 by three commits: the failing test (83b3e0b00, committed red), the fix (e08021412), and the pins for the boundary mutants (55b86a71e). Every figure below was taken at this head. `tools/pr/prepr.sh` was run once at this head; per the owner's 2026-11-07 ruling main was not merged again (merge-tree reports no conflict).

## Mutation proof

Red first: at 83b3e0b00 `python3 -I tools/plan/replan.py --self-test` printed `FAIL R10-BODY-CONTRACT's shape: 8 unmarked of 44 plan one part (19.8 h), not four: 79.2 44 carries, none measured as answered: 4 part(s)`, the same for the measured held group (`1 open carries at measurement + 6 appended since: 2 part(s)`) and the absorbed term (`30.0 ... + 3 absorbed carries`), then a TypeError on `build_plan(legacy=)`.

In-tree mutants added to the self-test's table, each killed (`python3 -I tools/plan/replan.py --self-test` prints `-> rc=1` for each, and `self-test: 0 failed`):

- `held-open-pending`: `return len(pending), ...` restored to `return len(group.get("carry") or []), ...` in `held_open` (the brief's first mutant) -> rc=1, failing the BODY-CONTRACT-shape arm and the two-part arm.
- `absorbed-pending`: `extra = len(pending) - ` restored to `extra = len(group.get("carry") or []) - ` in `group_hours`' absorbed-carry term -> rc=1.
- `appended-carries-open` (re-anchored), `held-measured-pending`, `pending-left-out`, `legacy-threaded` -> rc=1 each.

Diff mutants (owner ruling): `python3 tools/audit/seat/mutant_run.py --diff d84006e66...HEAD --cmd "env REPLAN_MUTATION_CHILD=1 python3 -I tools/plan/replan.py --self-test" --max-mutants 0 --report-only` over this round's added lines: 39 mutants, 15 survived, every survivor in a self-test fixture line (see `## Unpinned sites`); every production-line mutant (lines of `held_open` and the absorbed term) killed. The first pass left four production survivors (`i > cut`, `i <= cut`, `sum(2 ...)` in the measured count, the baseline default `0 -> 1`); 55b86a71e adds one arm for each and the second pass kills them. prepr.sh's own diff-mutant step ran with the same `MUTANT_CMD`; its line is in `## Figures`.

## Null control

- The carry text's null: the same two-part fixture with no carry marked (`["c"] * 9`) prices two parts (40 h), basis without "left out" (arm "the same carries with none marked plan two parts as before").
- Whole roster: the roster blob below with all 661 carry marks stripped, priced by the new head, gives a plan whose every group's `duration_minutes` and `finish` and whose `summary` equal the old head's plan on the marked blob (0 groups differ, summary equal). So the head's only change on real data is the marks.
- The unmutated copy of the self-test exits 0 (`null control: unmutated copy rc=0`).

## Figures

Roster: blob df4c1694f8b7ba59ba5144868a2b654b8bd32a56 (`origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`), two copies named `wave-r10-groups.json`; before = `python3 tools/plan/replan.py --roster-file <copy>/wave-r10-groups.json --start 2026-11-07T22:00:00` from a worktree of d84006e66, after = the same from 55b86a71e; same durations.json (unchanged by this diff).

- before: `summary: closure 2026-11-13T23:59:00Z | wall 145.98 h | CI 7537.5 min | batches 62 | stamps 5`; binding chain R10-BODY-CONTRACT -> R10-ARCH-DOCS -> R10-CLOSEOUT-CLEANUP, critical path 133.72 h, slack 12.26 h.
- after: `summary: closure 2026-11-14T00:51:00Z | wall 146.85 h | CI 7312.5 min | batches 60 | stamps 5`; binding chain R10-CLONE-2238 -> R10-ARCH-DOCS -> R10-CLOSEOUT-CLEANUP, critical path 112.6 h, slack 34.25 h.
- Closure delta: +52 min (later), not the verifier's -4h17m. Seat-minutes: R10-BODY-CONTRACT 4752 -> 1188 and R10-HANDOFF-PATH 4752 -> 1188 (7128 together, as the verifier said); all groups together 14464 fewer (also PREPR-CAP, ROSTER-WRITE-SWEEP, SAV-COMFORT, TICK-LEVELS, TRAIN-MERGE-LOOP to 0, and the absorbed term of ARCH-DOCS, FLOW-TOOLKIT-MODEL, ROUND-PLAYBOOK, USER-DOCS-VERIFY). Rule: per-group `duration_minutes` difference between the two plan.json files, summed.
- Why later: BODY-CONTRACT stops binding ARCH-DOCS (critical path -21.12 h), and ARCH-DOCS is then bound by R10-CLONE-2238, a coordinator group that waits for the coordinator cap 2 and finishes 11-11T19:39Z after, 11-11T13:53Z before. Isolated with a copy of the head whose absorbed term is restored to `len(carry)` (held-stage fix alone): closure 2026-11-14T02:10:00Z, binding chain the same. The coordinator queue order is not keyed on the realized binding chain; that is the scheduler's existing priority rule, outside carry 15 (see `## Forward-carry`).
- Merge-base control (the carry text): at the merge base dee8b413fd7d's own roster (blob c96d0d1eee72), before and after both print `closure 2026-11-12T15:16:00Z | wall 113.27 h`; R10-BODY-CONTRACT 4752 -> 4752 and R10-HANDOFF-PATH 2376 -> 2376, because that roster marks none of BODY-CONTRACT's carries yet and one of HANDOFF-PATH's 15 (2 parts either way).
- Self-test: `python3 -I tools/plan/replan.py --self-test`: `model self-test: 0 failed`, `self-test: 0 failed`, wall 68 s.
- Diff mutants (this round's lines): 39 mutants, 15 survived, wall 47.5 s (command in `## Mutation proof`).
- prepr.sh diff-mutant step (whole PR diff, MUTANT_MAX default 40): `WARN diff mutants 40 survivor(s)` (prepr.sh log, step "diff mutants"; the 40-mutant cap was spent wholly on the earlier rounds' tools/audit/seat/gantt_drift.py lines 41-124, which the replan self-test does not drive). Re-run against gantt_drift's own self-test, `python3 tools/audit/seat/mutant_run.py --diff $(git merge-base origin/main HEAD)...HEAD --path tools/audit/seat/gantt_drift.py --cmd "python3 -I tools/audit/seat/gantt_drift.py --self-test" --max-mutants 0 --report-only`: 107 mutants, 46 survived, wall 16.7 s; dispositions in `## Unpinned sites`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget touched.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (tests/entities.py, tests/harness_headers.py), run by prepr.sh.

## Unpinned sites

The 15 diff-mutant survivors are all in `selftest_model`'s new arms (lines of the fixture calls, not production code): `is_live` False -> True in a held-stage call (the held path ignores `is_live`: equivalent), `marked(0) -> marked(1)` (only the mark's hex value changes: equivalent), `carries_per_part 11 -> 22` and `["c"] * 9 -> 10` (still one/two parts: the arm's own cell), `open 5 -> 6` (min still 1), `<` -> `<=` on a float tolerance, and the date/round of the legacy plan fixture (not read by the arm). Disposition: equivalent mutants of test fixtures; no production site of this round is unpinned.

Earlier rounds' tools/audit/seat/gantt_drift.py (not this repair's lines, which the brief scoped to carry 15): of the 46 survivors under its own self-test, 40 are in its self-test body, its in-file mutant table and its argparse defaults (lines 133 onward); the production survivors are line 98 (the `key.split(":", 1)[1]` index swap in the silenced-key reader) and lines 121-124 (the state-file write in `main` and its return code), which no self-test arm drives. A tools/ site is outside `mutation-autofix`'s custom_components/ lane, so these need an in-tree arm; not built in this repair, left on this group (it owns gantt_drift.py) for its next round.

## Red checks

At head 55b86a71e: none concluded. The head has not run in CI yet (it reaches the PR when the orchestrator moves it), so no check run exists for it. At the PR head 0542969c3 (DIRTY, superseded by d84006e66 and this head), read with check-runs filter=all, all pages, in the previous body: `pr-contract / pr-contract` (body contract, answered by that body; cheaper detector `tools/pr/prepr.sh --body-check`, run for this body), `gate` (derived from pr-contract), `tests / nightly-status` (main's cancelled nightly.yml dispatch 42369836867, not this diff, non-required: never blocks per the owner's 2026-11-07 ruling). Earlier-head `gate` deferral reds belong to the gate instrument owned by R10-PROCESS-SLIM (#3245). Cheaper detector for a cancellation: none.

## Carry dispositions

0-based roster indices.

- Carry 15: implemented in this pull request (83b3e0b00 test, e08021412 fix, 55b86a71e pins). The orchestrator lands the mark.
- Carries 0, 2, 3, 8, 9, 10, 11, 12: built in earlier rounds (as the previous body). 1 and 7 moved to R10-BODY-CONTRACT; 4, 5, 6 dismissed as duplicates.
- Carries 13 and 14: not in this repair's brief (it scoped carry 15); left as they stand in the roster.

## Forward-carry

The +52 min closure is a scheduler property this diff exposes, not one it adds: the coordinator-cap queue orders by tier/critical-path/height computed without the cap, so a coordinator group that becomes binding (R10-CLONE-2238 here) is not promoted. A finding for the plan model's owner, which lands as a carry on this group in dev/programme/rosters/wave-r10-groups.json (the orchestrator writes it; no issue filed). Carry: R10-FLOW-TOOLKIT-MODEL

## Friction

- fixer-step-push: stale: refs/heads/handoff-wip/r10-flow-toolkit-model held a previous seat's BLOCKED commit 18b3f1d41 on 0542969c3, not an ancestor of d84006e66, so no step push could be a fast-forward; none was forced, and the ref is left for the orchestrator. Carry: R10-FLOW-TOOLKIT-MODEL
