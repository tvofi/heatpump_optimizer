R11-ADVISOR-MEASURES: the advisor's carried measurements (#3481 items 128b800e and c33b6f10), taken, and the card text corrected where the measurement contradicts it.

`dev/audit/harnesses/r11_advisor_measures.py` measures each carried item through the functions `async_simulate`'s branch calls (`whatif.schedule_days`, `price_tiles.schedule_figure`, `price_tiles.monthly_deltas(steady=)`), each beside a null. Two arms (`loop`, `pvloop`) add a truth the pair and the estimate are read against: the plan run closed-loop for four days after a warm-up, re-solved every four hours, with each loop's own stored-heat drift over its measured days bought back. Their null row, the hot-water setpoint moved half a degree, is the loop's own resolution, and a truth inside it resolves no sign.

What the measurement found, per item:

- **Carry 0, pair-other-asks (128b800e).** On a tanked house, the pair figure for the comfort weight and the lowest allowed temperature reads both signs depending on the hour asked (arm `asks`). The no-tank column reads the same, so the tank is not the cause: each plan is one day's, priced from the hour asked. `docs/dashboard-card.md` disclosed this only for a hot-water change. It now says the same of the weight and the floor. The hot-water setpoint asks also read both signs, and the closed loop does not resolve their sign either: both directions from 55 °C sit inside the loop's null. So the card's existing hot-water sentence stands as written. The hot-water minimum ask is the one the loop resolves (a cost), and the pair reads that sign at every row.
- **Carry 1, measured-fields x weekday-day (c33b6f10), throttling-valve two-tank house.** With weekend comfort set, every ask reads one figure across the seven days and none leaves the schedule branch. The weekend-day ask 22 → 23 °C reads a small saving on every day. The `holds` lines show why: the valve tops the rooms out between 22 and 23 °C. That is the case the card already discloses ("reads at or near zero, on either side of it"), so no text changes. Null: the same house without weekend comfort has no row against its ask.
- **Carry 1, pv-price (c33b6f10).** On the closed loop, the estimate's own-price end is closer to the truth than the mean-price end, both with the surplus and on the no-surplus null. So the card's sentence ("on a house with panels the lower end of the range … is the closer one") stands. Its PV day+1 truth sits inside the loop's null and resolves no sign. The `pv` arm also prices each schedule's reference-day thermostat at each step's surplus-aware price (`_energy_cost_fn`). That figure lies outside the estimate's range with and without the surplus, because the saved energy falls in the day's dearer steps; the card already says the degree tile differs from the estimate for that reason.

No production line changes: no measured figure is wrong against a truth that resolves its sign.

**Open for the orchestrator (pending ruling, not built here).** The pair figure for the comfort weight and the lowest allowed temperature moves with the hour asked (the `asks` rows against the ask, in `## Figures`), and the no-tank null reads the same. A figure that does not would need more than one day's pair per ask: more solves per what-if on a Raspberry-Pi-class host, or a cheaper estimate for these asks like the schedule one. That is a design choice outside a fixer's scope. This pull request discloses the scatter on the card and changes no figure. No live group or brief in the valid carry set receives it.

## Head

The code head `handoff/r11-advisor-measures` points at, `c716a4a1c0ede43088ebe7ebd1135ac7b828dacf`, measured on origin/main `e352724335c136b65562cd3e71f728549ad04a82` (2026-11-16T14:57Z). The harness runs were taken at the merge base `e352724335`; the head changes no production file, so they hold at the head.

## Mutation proof

n/a: no production line is added or changed. The only `.py` change is a harness under `dev/audit/harnesses/`, which `prepr.sh`'s mutant draw excludes. The card-text change is pinned by the harness rows it describes, not by a suite check: the `asks` arm's `against the ask` counts on the weight and floor rows are the measurement it states.

## Null control

- `asks`: the no-tank column (same weight and floor asks on the house without a tank) reads the same scatter, so the tank is not the cause. The half-degree setpoint row is the pair's own resolution.
- `loop`, `pvloop`: the half-degree setpoint row is the loop's own resolution. A loop truth whose magnitude is inside it resolves no sign, and this body states none from such a row.
- `valve`: the same house without weekend comfort has no ask against its sign and no ask that moves with the weekday.
- `pv`, `pvloop`: the same house without a surplus.

## Figures

All arms are run from the tree root with `PYTHONPATH=tests/hastub:tests:custom_components`. Each figure is a month's money in the fixture's price unit, and the arm named prints it:

- Rows against the ask, per pair ask, out of 18 (6 hours × 3 tank starts), and each ask's range: `python3 dev/audit/harnesses/r11_advisor_measures.py asks`. At `e352724335`: weight 5 → 2.5: 6 rows; weight 5 → 10: 5; floor 17 → 16: 8; floor 17 → 18: 3; hot-water minimum 45 → 50: 0. The half-degree null ranges −11.2 to +7.1.
- Closed-loop truths, and the null that is the loop's resolution: `python3 dev/audit/harnesses/r11_advisor_measures.py loop`. At `e352724335`: hot-water minimum +99.8; half-degree null −23.1. Every other ask's truth is smaller than the null.
- Valve two-tank house across the week, and what the valve holds: `python3 dev/audit/harnesses/r11_advisor_measures.py valve`. At `e352724335`: asks moving with the weekday 0; days leaving the schedule branch 0; weekend-day +1 ask against on 7 days at −0.9; held rooms at a 23 °C setting 22.10 and 22.07.
- PV estimate ends against the thermostat at surplus-aware prices: `python3 dev/audit/harnesses/r11_advisor_measures.py pv`. Against the closed loop: `python3 dev/audit/harnesses/r11_advisor_measures.py pvloop`. At `e352724335`, with surplus, day−1: truth −25.2, ends −63.2 and −8.0. On the null, day−1: truth −24.9, ends −63.2 and −26.8.
- Re-measured: the R10 instrument's arms `pair`, `fields`, `weekday` and `pv`, by `python3 dev/audit/harnesses/r10_advisor_steady_seams.py pair fields weekday pv`. At `e352724335`, `pair` reads both signs for both setpoint directions, `fields` 0 rows against on the two-tank valve house, and `weekday` 0 asks moving with the weekday.

<!-- figure-block: scope-line mb=e352724335c136b65562cd3e71f728549ad04a82 head=c716a4a1c0ede43088ebe7ebd1135ac7b828dacf -->
~~~text
MODE: SCOPED -- 4 script(s) run, 29 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

none
