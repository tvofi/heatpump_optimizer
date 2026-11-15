Design review: revise eb49f17976c34f6400a9d0e68c58d22f6523f4ee harness

Round 1. Reviewed from a detached worktree at eb49f17976 (one file, `design.md`), against base b3831ff64e and the predecessor heads the note names (cb6600d2f1, 92098a0099). Nothing was rerun but the enumerators the note's Figures name. Seat token count: the harness reports none.

## Revise points

1. `harness`: design.md:37 (3.1). The oracle is not yet the plan's. (a) The note names `step_duty` (`custom_components/heatpump_optimizer/pump_arbiter.py:509`) and `_step_kw` (`:652`) as the plan-side reader; both resolve the step through `_step_index(result, now)`, and `desired` (`:1291`) reaches `_step_kw` through `_space_target` and `_level_kw`, so an oracle that calls them shares the step selection with the write path and cannot move under U6's perturbation (the write landing one step late), the same ground on which the note voids `desired`. (b) "The arbiter's own table" is the module docstring at `pump_arbiter.py:13-25`: a document in the file under test, which an edit matching the code moves; `dev/governance/decisions/0018-objective-function.md:431` names exactly that edit as the gaming case and `:130-131` says "read from the plan and never from a document". Fix wanted: 3.1 states that the seat reads the step and its booked values off the solve result's own arrays without importing `pump_arbiter`, and states the duty-to-command mapping as the D16 brief's own invariants (the brief's wording, per plan state), citing the docstring table as a lead source only; or argues, with the perturbation that would show it, why sharing either does not void M2 and M3.

2. `harness`: design.md:60 (3.3). The cell formula is not stated, so the universe's count cannot be derived and its self-test arm cannot be written. "Cells are site times plan state, the states a tuple beside `CONDITIONS`" does not say whether duty modes and the four `CONDITIONS` (`tools/audit/enumerate.py:51`, crossed at `:122`, pinned by the arm at `:648`) leave the product; M5 and M6 (restart, unload, a duty-mode change) need some of them. The nine states are also not one axis: idle/both/hot-water only/baseline are duties, partial/full a level, boost and disinfection overlays, upgrade a lifecycle condition, so U2's input (a boost over a partial step) and U9's (minimum power on a cold tank) are no cell of the list as written. Fix wanted: one line giving the product (`sites x ...`), which existing factors stay, and per state the plan that realises it, such that each card of F5 names its cell.

3. `class-open`: design.md:83 (section 5). The grep's path list leaves out `dev/governance/roles/`. `dev/governance/roles/COMMON.md` at cb6600d2f1 carries two per-dimension lists the design changes the truth of: line 22, "If your brief makes you read `docs/` (D5, D6)" (D17's oracle is read from `docs/` and `README.md`, 3.4), and lines 29-30, "an isolated worktree for that purpose (D3, D11, and D0/D9 when instrumenting)" (3.4 puts D16 in ISOLATED for exactly a one-line production edit). Fix wanted: add the directory to the grep and say, per line, edited (with its `policy_lint.mjs --budgets` row) or left with the reason.

## Decisions routed (no revise point)

- decision: orchestrator. Whether E11-U10 closes in this group (design.md:21). At the current eval/r11 tip 9de7c2bdc7 U10 and U5 are still `accepted` with path `dev/governance/dimensions/D16.md`; their `unowned` text now reads "no escape behind it" (revision_3).
- decision: orchestrator. Which carry this merge discharges (design.md:109, item n5).

## Checked against the tree and held

- F1, F2, F3: `enumerate.py d16-writes` prints 38 lines (8 write, 30 hold), 456 with `--cells`; `d17-features` 307, in the seven prefixes 3.4 assigns (all seven are assigned once). The forecast read at `coordinator.py:7047` is listed as a write; the handed-on reference at `coordinator.py:3424` is not listed.
- F4 at 92098a0099: `CLAUDE.md` 3604 of 3605, corpus 69971 of 69971.
- F5: nine U cards, all accepted, at ca3f872430 and unchanged in `decision`, `ruling` and `paths` at 9de7c2bdc7; `review` reads approve of 02a48db212 at both. Every card names D16.md or D17.md, so dropping the prefix fold is right.
- CADENCE: `check-wave-script.mjs:971-972` at cb6600d2f1 refuses a driver naming one. The report schema and the driver's pattern admit 16 and 17 at cb6600d2f1 (not at b3831ff64e or 92098a0099, so the claim holds only once FINDER-CONTRACT merges, which the group's `After:` already requires).
- D1 step 2 at 92098a0099 (`D1.md:37-39`) carries the previous-release hold, as 3.2 argues. `PumpCommand` (`pump_arbiter.py:312`), `coord_all_features` (`tests/golden.py:914`) exist.
- `scopes.json` supports the `axis` block D17 uses; `check_scopes.py:749-750` already plants the overlap and the orphan for D1 and D2, so the two new arms repeat existing behaviour and rely on no new grader behaviour. `enumerate.py --briefs` reads only `--cells` and `--pairs`, so a `--kind` citation grades as the bare universe.
- Boxes: `boxGaps` (`audit-find.js:133-149` at cb6600d2f1) refuses more than three heavy seats and a Chromium seat with company; three heavy seats on B11 and on B13 pass it by reading. Not run (item n4 stands).
- Cost: L fits; no production code moves.

## Notes for the fixer

- The note names eval/r11 tip ca3f872430; the tip is 9de7c2bdc7 (revision_3: figures re-measured, U5 and U10 reworded, the review field unchanged). Re-read the cards there and name that sha in the body. Carry: R11-PRE-NEW-DIMENSIONS (item r1)
- D17's `kind` axis in `scopes.json` is a second copy of the enumerator's line prefixes; a prefix added to `d17-features` would have no seat and `check_scopes.py` would still pass. Add a self-test arm that the two sets are equal, with a planted extra prefix as its control. Carry: R11-PRE-NEW-DIMENSIONS (item r2)
- Open designs R11-PRE-STANDING-SCRIPTS (d1a4ae6a74: `CLAUDE.md`, `policy_budgets.json`) and R11-PRE-SHARED-FILES (281e74a24e: `CLAUDE.md`, `tests/closures.json`) touch this group's hot files and are not in section 7's list; no seam is claimed twice, but `CLAUDE.md` has one token of headroom, so the later merge re-measures. Carry: R11-PRE-NEW-DIMENSIONS (item r3)
- The other four open design refs (R10-START-COUNTER-EDGES, R11-OUTSIDE-HONEST-STARTS-RUNS, R11-PRE-PARALLEL-PIPELINE, R11-PRE-TOOLCHAIN-PIN) share no file this design edits beyond `policy_budgets.json` and `selftest_closures.json` rows of their own. Carry: dismissed: no shared seam (item r4)
