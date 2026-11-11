# Design: R10-ADVISOR-STEADY-START — the what-if's steady-start estimator (#2257), re-cut

**Re-cut after three revises** (design-review.md, "Three notes at most"; verdict design-verdict/R10-ADVISOR-STEADY-START 05e5b517b10e on e057b2ee2914). Base: origin/main f24d107bd7aa170bea7419251a4b7f4f48b732f6; no predecessor (`after` is empty), so no handoff head. Built work: handoff-wip/r10-advisor-steady-start, estimator head 273079db5; the verdict's `git diff --stat` over this note's hot files between its review base 45a8b828a41f and f24d107bd7aa prints nothing (re-run here), so a line cited at 273079db5 stands at the base. Main carries none of the built work: custom_components/heatpump_optimizer/whatif.py and the held-start flag exist only at 273079db5.

This note is **Part 1**: what the finder's harness measures. Section 3 names what left it. The shape that rounds 1-3 settled is not restated: it is sections 1-6 of design.md at d2d663c32a87 (approved, verdict 0fdadfe92458) and A3-A4 of design.md at e057b2ee2914, both in this ref's history, changed only where sections 2-3 below say so.

## 1. The harness, before any remedy
**Finder's harness:** dev/audit/harnesses/r10_advisor_residue.py, arm `arm_whatif` (direct optimizer solves on `r10_advisor_degree`'s fixture: the null and the varying series, three instants, three starts, the two degree asks of `price_tiles.specs` and two caps; 24 rows, 72 figures).

**Failing on today's main** (f24d107bd7aa, this seat, 45 s): `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_residue.py whatif` prints `whatif rows 24 plan_moves_by_start 24 held_moves_by_start 0`, caps `figures reading a saving (< -1) plan 18/36 settled 1/36`, and `VERDICT whatif the plan figure moves with the start; the held figure does not`. Read off its rows: the plan figure (what the panel shows, heatpump-optimizer-card.js:13318 `result.monthly_cost_delta`) has the held figure's sign on 36 of 36 degree figures and spreads up to 132.0 by start; the settled figure (what the fuse advisor reads, coordinator.py:9003) is against the held sign on 11 of 36 (varying 00:00 target_minus_1 +24.6 +24.7 +24.7, target_plus_1 -25.5 -21.7 -25.0).

**Null control:** the held figure, in the same loop: spread 0.00 on all 24 rows, sign right on 36 of 36 degree figures, +0.0 on all 36 cap figures. The arm prints `INVALID: the held control moved` and fails if it moves. The null series (flat price, constant outdoor) is half the rows.

**The same harness at the built head** (273079db5, this seat): `whatif` prints `steady rows 24 steady_moves_by_start 0 degree figures against the held sign 0/36 cap figures reading a saving (< -1) 0/36 cap range -0.7..+46.0`; `steadysign` (the fixer's arm in the same file, every second hour, 48 degree rows) prints `steady_wrong_sign 1 held_wrong_sign 0`: varying 05:00 target_plus_1 held +61.5, steady -0.1. So the built figure (the steady pair's spend plus deferred) fixes the spread and the caps, and the harness sees its sign turn on a degree ask at 1 row of 48. **The 6 of 24** (design.md A0 at e057b2ee2914) are read by the carrier script on the coordinator fixture, which is not this harness and not in the tree: they are evidence for Part 2, not a measure of Part 1.

## 2. The remedy Part 1 keeps: a schedule ask reads the thermostat pair, every other ask the steady pair
One branch in `price_tiles.monthly_deltas` (price_tiles.py:96-120 at 273079db5; signature unchanged, pure). With the steady pair present, the steady key's value is:
- the thermostat figure (the what-if's `baseline_cost` less the live's, plus the what-if's spend outside its solve, per month) **when that thermostat difference is not 0**: the ask moved what a thermostat would hold;
- otherwise the built figure, unchanged to the cent: the steady pair's spend plus `deferred_energy_cost`, what-if less live.
Without the pair the key is absent, as built (the failure rule stands).

Why this and nothing finer: it is the only comfort figure the harness has a null for. `baseline_cost` is a thermostat simulation from its own held start (optimizer.py:5665 at 273079db5), not a solve, so the two-solve basin spread that A1 measured (about 1 a day on a signal of 0.3 to 1) cannot reach it at any ask size; there is no ratio, no bound and no noise floor to size. Measured today: held spread 0.00 and sign right on every row of both arms (36 of 36 on main; 48 of 48 at 273079db5); cap asks read held +0.0 on 36 of 36, so they take the second branch, whose figures section 1 measured (0/36 saving, spread 0).

**Stated, not hidden.** (1) On a degree ask the panel now reads the degree tile's figure for the same ask, not "the plan's own answer": round 2's "tile and panel differ by design" is withdrawn for Part 1, and where the comfort floor stops the plan following the schedule down the figure overstates the saving (A2 at e057b2ee2914 measured delivered at 0.25 to 0.91 K per kelvin asked). That is routed decision 1, carried below, not ruled here. (2) An ask that moves the schedule and something else is priced by the thermostat only (A2's mixed-ask rule, unchanged): routed decision 2, carried. (3) The steady pair is still solved on a schedule ask, though that ask does not read it: the cost stays the settled bound (3 solves on a first what-if, 2 on a memo hit; `SIMULATE_MIN_INTERVAL_SECONDS` at coordinator.py:11191 and the `limited=False` path untouched), and skipping the pair is Part 2's saving to take with its own count check.

**Changes against the built work at 273079db5** (everything not listed is KEEP per A3 at e057b2ee2914):
| file | change |
|---|---|
| price_tiles.py `monthly_deltas` | the branch above |
| price_tiles.py module docstring, lines 20-30 | the cap paragraph says which asks read the pair and that a schedule ask reads the thermostat figure (item docstring-half) |
| optimizer.py `OptimizationResult` | **no new field** (A3's reference mean leaves with Part 2) |
| docs/dashboard-card.md:619-622 and the what-if section | "that panel prices the change in steady state: a comfort change as a thermostat holding the new schedule would pay, the same figure as the degree tiles; any other change on both plans started as if each schedule had been held. Neither includes the one-off coast or heat-up." Drop the built text's "about half the tile". |
| tests/features.py `_st_` block (31307-31716 at 273079db5) | the numbers check on `monthly_deltas` gains the thermostat branch with stub results; the sign check at 31370-31376 stays and turns green; A4a and A4b as written, with item recite-a4 |
| dev/audit/harnesses/r10_advisor_residue.py | KEEP as built; no new file |
| tests/structure_budgets.json | re-measure; if a cap is met, pay or report before the push, never raise |
| BLOCKED.md on the wip ref | DROP |

Callers (unchanged from round 2's table): the card and the fuse advisor ask `steady=True` and read the steady key; the cap tile reads it through `price_tiles.monthly_figure`; the degree tiles and `_solver_smoke` ask `steady=False` and read what they read today. `monthly_cost_delta`, `monthly_held_cost_delta` and `monthly_settled_cost_delta` keep their meaning.

**Alternatives, lost.** *The pair's spend plus deferred for every ask (as built):* `steadysign` reads 1 of 48 against the ask, and no difference of two independent solves' money is sign-safe (A1). *Delivered kelvins at the thermostat's price (A2):* its ratio is unmeasured at the panel's asks and its bound has no measurement (verdict point 1); Part 2. *No money line on a schedule ask:* the owner ruled a figure, not a disclosure (2026-11-01), and it removes the money from the panel's commonest ask. *Branch on the override keys instead of the thermostat difference:* puts the list of schedule keys in a second place beside `price_tiles.specs` and the optimizer's comfort bounds, and misses a key added later.

**Sibling sites** (verdict, "Checked, no revise", step 3, at 273079db5): cross-solve money differences are price_tiles.py:110, :111-113, :117, :119 and coordinator.py:11216; steady-key readers price_tiles.py:153, coordinator.py:8977, card :13326, tests/features.py:31252, r10_advisor_residue.py:136 and :215. The branch sits at :111-113; no reader changes.

## 3. Evidence, by file; all of it this harness or the suite
- **Failing first.** (a) `r10_advisor_residue.py whatif`: red on main as section 1 (24 of 24 move; 18/36 and 1/36 cap savings), green at the head: `steady_moves_by_start 0`, `0/36`, `0/36`. (b) `r10_advisor_residue.py steadysign`: red at 273079db5 (`steady_wrong_sign 1`), green at the head (0 of 48), where the check is the steady figure against the **ask's** direction (`steady * want`, r10_advisor_residue.py:217 at 273079db5), not against the held figure. (c) tests/features.py: the sign check at 31370-31376 (red at 273079db5 per A3) and round 2's spread, cap, cost, caller and failure checks (section 5 of design.md at d2d663c32a87). (d) tests/card.mjs: the summary renders money only from the steady key; no key or no draft renders no money and no caveat.
- **Null controls.** Held spread 0.00 and `held_wrong_sign 0` in both arms; the null series reads one steady figure at all three starts; **every cap figure of `whatif` and of the cap and fuse checks is identical to the cent at 273079db5 and at the head** (the branch touches no ask whose thermostats agree: the control that the remedy moved only what it claims); the idle panel renders nothing.
- **Mutants a reviewer runs.** (1) branch removed (as built): `steadysign` red at 1 of 48 and the 31370 check red. (2) branch taken for every ask (condition dropped): cap figures read 0.0; the cap check, the fuse check and `whatif`'s cap range are red. (3) thermostat read with the sides exchanged: every degree row red. (4) the outside-solve spend dropped from the thermostat branch: the numbers check red. (5) the branch falling back to the thermostat figure when the pair is absent: round 2's failure check red (key must be absent).
- **Goldens.** As round 2: none carries a monthly key; a moved fixture is claimed per claim-files.md, never re-recorded.

**Left this design as Part 2** (not measurable with the harness above; each carried below): the delivered-kelvins figure and its reference-mean field; the panel's own asks (0.5 K, one hour of the day window) and the bound's noise floor; the under-bound ask; the carrier script and A1's table landing as a harness; the twelve-hour coordinator-fixture check; skipping the unread pair.

## 4. Hot files, position
As section 6 of design.md at d2d663c32a87; optimizer.py is touched only by the built held start. After: none. Closes #2257; `fixes` must list 2257. Size stays L: one branch on built work.

## Notes for the fixer
Later parts, out of Part 1:
Carry: R10-ADVISOR-STEADY-START (item part2-delivered) - the panel pricing a comfort change as kelvins delivered at the thermostat's price (A2 at e057b2ee2914) needs first the panel's own asks in the harness loop (comfort +0.5 and -0.5 through `target_temp` and `comfort_temp_day`; day start and day end one hour each way), the zero ask on two instances as the noise floor, and the bound set from that floor (verdict point 1).
Carry: R10-ADVISOR-STEADY-START (item part2-underbound) - what an ask below that bound shows, with its check and mutant (verdict point 2); under Part 1 it reads the thermostat figure.
Carry: R10-ADVISOR-STEADY-START (item part2-carrier) - the appendix script of design.md at e057b2ee2914 lands as a harness with Part 2; the 6 of 24 on the coordinator fixture and A1's carrier table are its evidence, re-measured then.
Carry: R10-ADVISOR-STEADY-START (item part2-skip-pair) - a schedule ask does not read the pair it solves; skipping it saves two solves and owes a count check.
The verdict's routed decisions, carried, not ruled:
Carry: R10-ADVISOR-STEADY-START (item panel-meaning) - decision: orchestrator. What the panel's comfort figure means; Part 1 ships the thermostat figure (section 2, stated 1) and the docs say so.
Carry: R10-ADVISOR-STEADY-START (item mixed-ask) - decision: orchestrator. A panel ask carries comfort, hot water, the day window, quiet windows and wood slots together (card :13229-13236 at 273079db5); under Part 1 any ask that moves the thermostat is priced by the thermostat alone, so a cap or quiet-window change sent with it adds nothing. Accepted, disclosed or priced.
The verdict's carries (05e5b517b10e):
Carry: R10-ADVISOR-STEADY-START (item recite-a4) - A4's two cites are exchanged at 273079db5: the `topology_layout` assignment of `_st_optimizer` is tests/features.py:19263 and `_fake_simulate` is :31421, as the verdict states them; re-cite both at your merge base.
Carry: R10-ADVISOR-STEADY-START (item ratio-pin) - Part 2: the ratio is pinned by a fixture solve (a minus row's figure smaller in magnitude than its held figure where the floor is in reach), not a stub. In Part 1 the same rule binds mutant 3 and 4's checks: a solve, not a restated formula (tests/README.md).
Carry: R10-ADVISOR-STEADY-START (item docstring-half) - price_tiles.py:28-29 at 273079db5 ("the plan's own answer to the same degree, about half") is false after section 2; rewrite it with the docs sentence.
Carry: R10-ADVISOR-STEADY-START (item result-overlap) - Part 1 adds no field to `OptimizationResult`; Part 2's field meets design/R10-CLONE-2238 and design/R10-WHY-NOW-WIDGET there.
Carry: R10-ADVISOR-STEADY-START (item floor-zero) - with the live schedule at `min_temp` or heating off the thermostat difference is 0 and the ask falls to the pair; state in the check what the card renders for a pair figure near 0 there (`whatif.same_cost` or money); this note did not read that threshold.
Carry: R10-ADVISOR-STEADY-START (item horizon-mean) - Part 2: take the bound's measurement at the fixture's horizon and say so.
Standing, unchanged: round 2's verdict carries (const-comment, recite-916, whatif-instance, rebind-local, helper-weather, memo-state, text-overlap, attr-sites; 0fdadfe92458), the round-2 note's own (recite, fuse-key, fuse-none, tile-callsite, memo-key, test-attrs, stubs, locales, module-docs; d2d663c32a87) and A6's worker-patch and two-zone-mean (e057b2ee2914; both Part 2).
Carry: dismissed: measured in section 1, one of 48 (item pair-for-all-asks)
Received: carry 0 of this group (from R10-ADVISOR-WHATIF, #2963).

Seat tokens: not reported by the harness for the seat; its one extraction subagent reported 41118.
