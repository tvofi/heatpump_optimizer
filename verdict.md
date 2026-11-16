Design review: approve ce85b100490363e0ffd6afbbcd9aa3ec334abc50

Design reviewer seat, round 2, for R11-OUTSIDE-HONEST-DHW-RUNS (group B of outside pull request 3529 by Bankaifan). Reviewed from a detached worktree at ce85b10049; judged against 54cb7211642364d762ba47f42d5f7b8a5953f742 (`origin/main`). Previous verdict: 9e83557135, `revise` on f7d50191e3. Nothing rerun: there is no code, and the note's spikes (items s1, s7) are in no tree.

## Round 1's three points

1. Answered as asked. design.md "Acceptance" and "Commit stage" steps 3 and 5: the lifted plan is a candidate only if `drop_unstartable` leaves it unchanged on its own walk and `_dhw_shortfall` is no higher than the uncommitted plan's; the uncommitted plan is the only unconditional fallback. `place_startable` ends in `drop_unstartable` (`dhw_planner.py:313`), so that fallback is startable where a start condition is known. The correction to round 1's table row 3 (the lifted plan under `_ctx_clamp`, 1 of 2) is the designer's spike and was not rerun; test 2d pins the clause it rests on.
2. Answered. Test 2 has an arm per mutation: 2a the boolean (rounds counted, a committed plan ships), 2b the start clause called directly, 2c the lifted plan's pass through the acceptance with its halved-lift null, 2d the shortfall clause. Each mutation target in "Mutation targets" names its arm.
3. Answered by the first arm. `runs._advance` (`runs.py:210`) and the read-back in `commit` (`runs.py:156`) stay the one kernel, generalised over actions and a cell rule its caller supplies; the leaf holds an opaque scalar and the per-step start boolean reaches it through the move rule (`runs.py:191`). Checked in the tree: `_advance` is 38 lines, called once (`runs.py:150`); `git grep -n "_advance(\|_moves(" 54cb721164 -- custom_components` prints `runs.py` only; `git grep -n lexsort 54cb721164 -- custom_components` prints `runs.py:241` only, so no second cheapest-per-cell program exists to fold in. `commit`'s signature and masks are held by test 3 and the space-only null.

## Checked, no point

- Base: the note names 5854e4f69e, an ancestor of 54cb721164; `git diff --stat 5854e4f69e 54cb721164 -- custom_components tests/features.py tests/seam_map.json dev/audit/harnesses dev/programme/rosters dev/governance/dimensions/D7.md` prints nothing. `VERSION` is 10.0.2 at both.
- Line citations resolve at 54cb721164 to the symbol named: `dhw_planner.py` 245, 270, 300, 1141, 1301, 1429, 1496, 1655, 1712; `optimizer.py` 175, 190, 194, 401, 462, 544, 2040, 2064, 3984, 4372, 5747; `runs.py` 156, 191, 210; `thermal_model.py:2138`.
- Seam: the planner owns the store, the transition, the bounds and the acceptance; the leaf owns lengths, moves, tie break, start count and the kernel; `optimizer.py` is a caller at three sites. No new write path into another module's state. `_engaged` (`optimizer.py:194`) is `cycling_cost > 0` or a clamped install, as the note reads it.
- Sibling sites: the four greps reproduce (four `_dhw_build(` calls and the definition; 18 `min_run_power` lines, all `dhw_planner.py`; one `DhwPlanner(`; the kernel's two callers above).
- Bindings 1 to 6 of the dispatch brief each have their answer in the note: acceptance and boolean (1), the store's one holder with the linear program's inline store moved to a helper both read (2), the exchange's rounds uncommitted and one committed build after (3), the ranking's start count on the combined draw and no stop term (4), the tie break called and not owned (5), the three body items with a reason or a measuring test (6).
- Evidence: test 1 fails today on its assertion (14 and 10 steps under the floor at the base, the note's spike). `dev/audit/harnesses/r11_honest_starts_runs.py` has `fixtures`, `stress` and three installs (`:112`, `:487`); `dev/audit/harnesses/r10_combi_tank.py` has `exchange` with its zero-round null (`:201`). `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt` are the right claim files.
- Designs in flight: of the 18 `design/*` refs, only this one and its parent (R11-OUTSIDE-HONEST-STARTS-RUNS, merged as pull request 3602) name `runs.py`, `dhw_planner.py`, `_advance`, `_moves`, `_combi_flux_exchange`, `_dhw_build` or `_realize_joint`. R11-OUTSIDE-HONEST-METERED-FLOOR names none of them.
- Predecessor: R11-OUTSIDE-HONEST-STARTS-RUNS-P2 has no handoff head; its work in progress dbc806ce5f leaves `runs.py` untouched (`git diff --stat origin/main...dbc806ce5f`).
- Cost: three production files, one test file, one harness. The `runs.py` churn is stated (the kernel's signature and about a third of its lines, `commit`'s loop, the read-back as a function); sizing it is routed below.

## Decisions

- decision: orchestrator. Size, with point 3's churn on `runs.py` as the note states it.
- decision: orchestrator. The settle and the unengaged double heating as a group of their own, as the note routes it; round 1's observation stands (combined draw under the floor can still ship on an engaged combi install after B, as at the head).
- decision: owner. The clamped tail, after test 7's figures.
- decision: orchestrator. `git grep -l "HONEST-DHW-RUNS" 54cb721164 -- dev/programme` prints nothing: the dispatch payload is still the group's only brief, and carries 1 and 2 name a roster the group is not in.
- decision: orchestrator. The fixer dispatches after R11-OUTSIDE-HONEST-STARTS-RUNS-P2 merges and the note is revalidated against its diff, as the note's "Hot files" states; this approve does not cover that revalidation.

## Notes for the fixer

Round 1's items r1 to r6 stand as carried.

- `drop_unstartable` indexes `start_below` (`dhw_planner.py:284`) and `dhw_start_temps` returns `None` where no start condition is known (`dhw_planner.py:237`), which is the case in every golden. The acceptance's start clause holds there without the call; a test with no hysteresis set pins it. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item r7)
- Test 2a's first assertion (no step under the floor) stays green under its mutation if the fixture's lifted plan is accepted, and its round count stays green if the loop leaves on a repeated plan as `place_startable` does (`dhw_planner.py:310`). Assert that the shipped plan is the wrapped program's last return, so the arm does not rest on either. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item r8)
- The null "engaged with a plan already at the floor or above and no start priced: arrays equal" holds only if the uncommitted plan, a candidate there as its own lift, outranks the program's plan. If it goes red, print both candidates' ranked cost and say which rule ships the uncommitted plan; the null is not weakened. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item r9)
- P2's work in progress dbc806ce5f changes `dev/audit/harnesses/r11_honest_starts_runs.py` and its mutants file as well as `tests/features.py`; the note says `tests/features.py` only. Test 7 reads that harness's installs, so the revalidation against P2's merged diff covers the harness. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item r10)
- The note does not state what the store program pays per start inside the kernel. The move rule prices every off-to-on edge of the hot-water plan, while the ranking counts a charge beside a space run as none (binding 4). Name the program's start price in the code and print, per fixture, the program's own start count beside the combined draw's. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (item r11)

Seat tokens: the harness reports none for this seat.
