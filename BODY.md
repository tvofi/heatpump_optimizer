R10-FLOW-TOOLKIT-MODEL: plan-model correctness in tools/plan/replan.py, plus the tracked Gantt-drift instrument (carry 12). Measures the roster/plan semantics only; no production code.

This repair round lands carry 16 (packet numbering; roster index 15; "From the s12 slip study (2026-11-07)"), on top of the merge-only conflict seat's head d84006e66001d42c744448949159f6473adedcd6, fast-forward. `git merge-tree --write-tree origin/main HEAD` reported no conflict at the start, so no merge was made.

Carry 15: `held_open` counted `len(group carry)` and `group_hours`' absorbed-carry term counted `len(group carry)`, so a carry `roster_edit.py mark-carry` had discharged (implemented, moved, dismissed) still priced as open work. Both now count `roster_lib.pending_carries` (unmarked and not legacy):

- `held_open(group, durations, pending)`: an unmeasured group counts its pending carries; a measured one (`held_open_carries`) counts `min(open at measurement, pending carries among those then held)` plus the pending carries appended since. With no carry marked this is exactly the old figure.
- `group_hours(..., legacy=None)`: computes `pending` once, prices the absorbed-carry term on `len(pending)`, and the duration basis ends `, N marked carries left out` whenever any carry was left out.
- `build_plan(..., legacy=None)` threads the cut-over through; `main` reads it with `roster_lib.read_legacy(repo, ROSTERS_DIR/<roster basename>)`, so a `--roster-file` copy named `wave-r10-groups.json` keeps its round's cut-over (`roster_lib.CARRY_CUTOVER`). A cut-over the clone cannot read refuses as a `PlanError`, never "no legacy".

`replan --measure-sizes` was not used (the verifier found it does not deliver the saving).

Earlier rounds (unchanged by this repair, kept from the previous body): carries 0, 2, 3, 8, 9, 10, 11 and 12 built; 1 and 7 moved to R10-BODY-CONTRACT; 4, 5 and 6 dismissed as duplicates; review items 1-5 and round-5 items 1-2 repaired, item 7 dismissed with its reason; the merge resolutions in `is_done`/`plan_page.py` are as described on the earlier heads.

## Head

55b86a71ea5752e1af9f6491a94798629df236b2, a fast-forward of d84006e66001d42c744448949159f6473adedcd6 by three commits: the failing test (83b3e0b00, committed red), the fix (e08021412), and the pins for the boundary mutants (55b86a71e). Every figure below was taken at this head. `tools/pr/prepr.sh` was run once at this head; per the owner's 2026-11-07 ruling main was not merged again (merge-tree reports no conflict). No step was pushed to refs/heads/handoff-wip/r10-flow-toolkit-model: it held a previous seat's BLOCKED commit 18b3f1d41 on 0542969c3, not an ancestor of d84006e66, so no push there could be a fast-forward, and none was forced.

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
- Why later: BODY-CONTRACT stops binding ARCH-DOCS (critical path -21.12 h), and ARCH-DOCS is then bound by R10-CLONE-2238, a coordinator group that waits for the coordinator cap 2 and finishes 11-11T19:39Z after, 11-11T13:53Z before. Isolated with a copy of the head whose absorbed term is restored to `len(carry)` (held-stage fix alone): closure 2026-11-14T02:10:00Z, binding chain the same. The coordinator queue order is not keyed on the realized binding chain; that is the scheduler's existing priority rule, outside carry 15 (see `## Forward-carry

none

## Friction

none
