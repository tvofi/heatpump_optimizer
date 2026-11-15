Design review: approve a9377bcf47957e63060733e61a9cb551a8734b1c

Round 2. Reviewed from a detached worktree at a9377bcf47 against b880dc914f (the note names b3831ff64e; between the two only `audit-find.js:188-189` and `finding.schema.json:95` moved, one class id added to the enum, which touches no claim of the note). Read: `git diff eb49f17976..a9377bcf47`, the tree at b880dc914f, predecessor heads cb6600d2f1 and 92098a0099 (neither is an ancestor of b880dc914f yet; the group's `After:` holds it), eval/r11 at 9de7c2bdc7. Nothing was rerun. Seat token count: the harness reports none.

## Round-1 points

1. `harness` (3.1): resolved. The oracle reads index k of `OptimizationResult`'s own fields (`optimizer.py:2292`; `power_schedule`, `dhw_power_schedule`, `optimal_setpoints`, `room_temp_trajectory`, `timestamps`, `duty_floor_kw` all exist there), the harness choosing k, so `_step_index` (`pump_arbiter.py:543`) and `planned_draw_runs` (`thermal_model.py:1260`) leave the oracle; the mapping is the brief's own eight invariants with the docstring a lead source; P1 and P2 are the perturbations and their null controls are stated.
2. `harness` (3.3): resolved. One axis, 14 named states, each with the plan that realises it; `PUMP_DUTY_MODES` (`const.py:1043`) and `CONDITIONS` (`enumerate.py:51` at 92098a0099) become rows; every U card of F5 names its cell (M2 to M4 table, U1 on D17's `option` line).
3. `class-open` (section 5): resolved. F6's enumerator returns exactly `COMMON.md:22` and `:30` at b880dc914f and cb6600d2f1; both edited with F7's row (`policy_budgets.json` keys it `tools/audit/briefs/COMMON.md`, 117 lines and 1756 tokens at cb6600d2f1); `D3.md:6`'s "the one finder" is untrue of `ISOLATED` (`audit-find.js:65` at cb6600d2f1) and is cut. `worktree` appears in D3, D9 and D13 only, as F6 says.

## Decisions routed (no revise point)

- decision: orchestrator. R11-PRE-PRODUCT-READS (design f5147c0e59, opened since round 1) reads `d16-writes --cells` strings as printed (its design.md:13 and :22: F3 reads 38 sites, 456 cells). This design changes each cell from `| duty=<m> | <condition>` to one state; any seed ledger that group lands keyed on today's strings is orphaned if it merges first. Order the two, or have the later re-key. Carry: R11-PRE-PRODUCT-READS (item r5)

## Notes for the fixer

- design.md:97. "refuses unless `observe`, `off` and `control` are all in it" is a subset test and does not do what the same sentence claims: a fourth duty mode added in production passes it and goes unrowed. Make the refusal set-equality between `PUMP_DUTY_MODES` and the duty modes the state tuple names, with a planted fourth mode as the arm's red control and today's const.py as its green. Carry: R11-PRE-NEW-DIMENSIONS (item r6)
- design.md:41 and :81. "zero or no less than twice the floor" holds for `partial` at (f+P)/2 only when P >= 3f (and for `full` when P >= 2f). The harness's configured pump states P >= 3f, or the cell books max(2f, (f+P)/2); the brief says which. Carry: R11-PRE-NEW-DIMENSIONS (item r7)
- design.md:58. P1 (step selection one step late) moves no cell when steps k-1 and k book the same state; the U6 cell's plan books step k-1 in a different state from step k (e.g. `idle` then `partial`), and the brief says so, else P1's red arm is green on the defect. Carry: R11-PRE-NEW-DIMENSIONS (item r8)
- Base moved b3831ff64e to b880dc914f with no hot-file change but the schema enum line; re-measure F1 to F7 at the merge base as the note already says. Carry: dismissed: no claim affected (item r9)

## Checked and held

- Sibling designs (step 5): the eight open `design/*` refs; R11-PRE-STANDING-SCRIPTS and R11-PRE-SHARED-FILES named in section 7; R11-PRE-PRODUCT-READS routed above; the rest share only their own budget and closure rows (round 1, item r4).
- Cards: eval/r11 tip still 9de7c2bdc7, `review` approve of 02a48db212; nine E11-U cards accepted, each naming D16.md or D17.md.
- Cost: L, no production code; no split needed.
