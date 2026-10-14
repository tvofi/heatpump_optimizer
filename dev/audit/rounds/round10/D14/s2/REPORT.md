# D14-s2 — round 10, baseline 17f1c55fad1b

## Method
M1: read dev/audit/config/bugclasses.json. Open production classes: P8 (8 instances, 6 rounds), N-name-sort (8, 6 rounds),
P10 (7, 6 rounds), plus four single-instance R9 classes. M2: picked P8 (most rounds tie; money = critical-class consequence).
M3: `p8_money_units.py` drives the real coordinator with a EUR/kWh price feed on a SEK instance and counts money surfaces
naming a currency other than the feed's; it also enumerates statically every `resolve_currency(...)` call that is not the
`feed or resolve_currency(hass)` fallback.

## Findings
**D14-s2-01 (P8, high, bug).** Property: every published money figure names the price feed's declared currency.
`HeatPumpOptimizer­Coordinator._narrative_view` passes `resolve_currency(hass)` (instance label) to `narrative.render`,
while every sensor unit uses `coordinator.currency` (feed first, #1657). EUR feed on SEK instance: 3/3 narrative lines say
SEK for EUR amounts; sensor units say EUR. Null control (SEK feed): 0. Perturbation: patch
`coordinator.resolve_currency` to return the feed code → 0. The `narrative.render` docstring claims the two "are the same
decision", which #1657 made false.
Seams listed (9): coordinator.py:10456 (instance — measured); coordinator.py:1979,1992 (guarded: the mismatch repair issue,
by design); config_flow.py:553 (money field labels), 3736/3737/3795/3796/3777 (grid-fee bound and rule parsing in the
instance currency while coordinator.py:7068 checks the same fees against `self.currency` — divergent precedence, not probed).
Barrier proposal: a `tests/` arm (entities.py P2-style) running this replay over every money surface, plus a structure rule
refusing `resolve_currency(` outside currency.py except in the `x or resolve_currency(...)` form and the repair issue.
Gate cost: < 2 s.

## Non-findings
- coordinator.currency follows the feed: coordinator_unit_mismatch=0 (same command).

## Unfinished
- M3 re-find at pre-fix commits (3490cb16 etc.) not run; no clean-fixture-over-pre-fix comparison.
- N-name-sort and P10 not picked; M4/M5 for detector/barriered axes not swept.

## Exposure
bugclasses.json (all classes, P8 instances and detector_idea); git log --grep=1657 (7cccba3a7 F1.8); git show -s eaa2a06, 3490cb16.

## Harness
`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/s2/p8_money_units.py [--perturb]`
