A room-temperature listener, modelled on the peak guard, switches a space-heating pump off once inside a plan interval when the room passes its threshold. The next cycle's own switch write resumes it. Decision on #201 (comment 6067353918, mandate 6067089637); the rule choice was recorded on #201 after the comparison below. This is the last PR of the live-fix wave. Its learner-freeze order (amendment A2 of the wave's design note) is already carried to fix 5.

**Shipped rule: plan-aware.** Threshold = max(active comfort target, the plan's predicted room at the end of the current step) + 0.5 K. **It was inert in every measured case and ships as a guard.** In each scenario below the 30-minute re-solve already had the pump off before the room passed the threshold. The measured overshoot goes into the floor store, which is fix 5's (the slab observer), not this one's.

Rule comparison, closed loop stepped per minute through the production listener (`dev/audit/harnesses/early_cutoff_closed_loop.py`; "warm+on" = minutes the room was above target + 0.5 K with the pump on):

| variant | no cut-off | plan-aware (ships) | literal: target + 0.5 K | middle: literal, exempt steps the plan predicts above target |
|---|---|---|---|---|
| NULL (plant = model) | 0 cuts, 2.0 kWh, room 20.11-21.02 | 0 cuts, 2.0 kWh, 20.11-21.02 | **2 cuts, 1.4 kWh, 19.99-21.00 (fails the null control)** | 0 cuts, 2.0 kWh, 20.11-21.02 |
| LIGHT (room 0.15x the model's mass, -2 degC) | 26.6 kWh, 5.82 h >21.5, max 22.60, warm+on 54 min | 0 cuts, unchanged | 5 cuts, 24.0 kWh, 0.00 h >21.5, max 21.11 | 0 cuts, unchanged |
| OWNMIN (the finder's pump >= 3 kW) | 2.5 kWh, max 21.06 | 0 cuts, unchanged | not run | 0 cuts, unchanged |
| HOT (>= 6 kW, COP 1.4x) | 3.0 kWh, max 21.43 | 0 cuts, unchanged | not run | 0 cuts, unchanged |
| SUN (600 W/m2 unforecast, 12 degC) | 2.0 kWh, 12.70 h >21.5, warm+on 0 min | 0 cuts, unchanged | not run | 0 cuts, unchanged |
| COLDSUN (same sun, -2 degC) | 18.4 kWh, 10.77 h >21.5, warm+on 0 min | 0 cuts, unchanged | not run | 0 cuts, unchanged |

The literal rule acts on LIGHT, but on NULL it cuts a correct plan's night-to-day pre-heat (threshold 20.0 at the 19.5 night target), so it does not ship. The middle rule passes NULL but does not act on LIGHT, so by the recorded decision plan-aware ships. The review of round 1 reproduced every figure in the table.

What the cut-off does and leaves alone (`custom_components/heatpump_optimizer/early_cutoff.py`):
- **Inputs.** It takes the `arbiter_inputs` callable, the boost record and the optimizer config. Only `state_for` keys on the coordinator (rule A). It reads its configuration through #1745's `EntryConfig` (indoor thermometer, switch, defrost flag, interval) and never a raw key; it is on `tests/entities.py`'s migrated list.
- **One switch writer.** `on_off_service` (the #1526 domain router) and a new `switch_supply` move from `coordinator.py` into `pump_arbiter.py`, which takes values. The cycle's plan write and the cut-off both call `switch_supply`, so the switch has one writer and the routing has one owner. Three records follow the router: P2 `entity_write_domain`'s owner is now `pump_arbiter.py::on_off_service`; its mutation-ledger pin (`RETURN_DEL dac85d34`, the same line) is re-keyed there; and the finder's D12-s2 harness (`surfaces.py --perturb`) now patches it. Normal plan writes are unchanged: the review's run of that harness shows identical cells at both ends, and `--perturb` still turns 0 failing cells into 2. Alternatives considered: keeping the router in `coordinator.py` and importing it from the cut-off is an import cycle; handing the cut-off a coordinator callback re-creates the coordinator dependency rule A forbids.
- **Short cycles.** It does not cut a pump that has been on for under 10 min (`MIN_ON`; a missing or future switch stamp counts as an unknown run). It does not cut with under 10 min to the next scheduled cycle (`MIN_OFF`), and it cuts at most once per cycle. **An early refresh** (a mode change, a manual plan, a button) inside `MIN_OFF` of a cut keeps the pump off (`allow_on`, read in `_apply_action` where the plan's on/off is taken). It is let through at once on a step the cut-off would not touch (a boost, hot water, a non-plan mode). Such a refresh therefore defers the resume to the following scheduled cycle. All of this arithmetic is in UTC, pinned across both 2026 DST changes in `tests/dst_checks.py`.
- **Scope.** It acts only on a `step_duty == "space"` step. Exempt: hot-water, both and idle steps, a boost on either channel, disinfection, a running defrost, a tank below its minimum, non-plan modes, a stale plan and a cold lower zone. The arbiter writes nothing while the switch reads off, so it cannot re-enable the pump within the cycle (checked, with a positive control). The ECL110 displacement and the peak guard keep their own writers.
- **Margin.** 0.5 K, a constant. An options field would move `tests/golden/config_flow.json`, which only a claim can, and add a string to both translation files.
- **Learners.** A cut interval freezes them under one reason, `early_cutoff`, for the cut cycle and the next. **Order: `_tail_freeze` returns the cut reason before the unmetered-power freeze** (A2: the slab observer ignores only the unmetered reason). A check fails if the order is reversed.
- **Diagnostics.** The `(key, view)` loop in `diagnostics.py` (S7) carries an `early_cutoff` row: margin, minimum times, `cut_this_cycle`, `interval_cut`, count, the last cut (time, room, threshold, switch) and `last_held`. Each cut is logged at INFO.

**Structure.** `max_class_loc` falls 8817 -> 8810 and is re-recorded (the coordinator's switch write is now one `switch_supply` call, and the arm is one delegation); every other row is unchanged.

**Architecture score: `coord_footprint` 2587 -> 2589 (WORSENS, +2), each piece admitted by the wave's design note:**
- the class: -1 (the switch write's try/except becomes a delegation, offset by the one arm statement);
- `early_cutoff.state_for`: +1, rule A's one coordinator-keyed function, cut from 3 statements to 1 (`setdefault`);
- `coordinator._tail_freeze`: +1, A2's freeze order;
- `diagnostics._coordinator_snapshot`: +1, S7's view row.

## Head

`3ecb86adaf247f182679a175bd619fd363a5e35c`. Since round 1's reviewed `b731ef6b3`, one commit, `3ecb86ada` (round 2): the moved router's ledger pin re-keyed, the D12-s2 harness retargeted, the cycle's refresh hold pinned. Round 1's commits on top of `f74924e09`: `c3d16ace9`, `d02f851e1`, `b731ef6b3`. Measured 2026-10-09.

## Mutation proof

Each mutant was applied at the head and the early cut-off feature section driven (M13: the DST section, under `HASTUB_TZ=Europe/Stockholm`). Every one turns at least one check red; M0 and M0d (no change) fail none.

- M1 drop the once-per-cycle latch: 3 failed, incl. "a second warm reading in the same cycle writes nothing more"
- M2 `room <= limit` to `<`: "a room exactly at target + 0.5 K does not cut (the margin is inclusive)"
- M3 any duty instead of space-only: "a hot-water-only / both / idle step is never cut, however warm the room"
- M4 drop `MIN_ON`: "a pump on for less than MIN_ON is not cut"
- M5 drop `MIN_OFF`: "with less than MIN_OFF to the next cycle the pump is not cut"
- M6 drop the plant exemptions: "a tank below its minimum exempts the step", "a running defrost is never cut"
- M7 drop the freeze reason: "a cut interval freezes the learners under the one early_cutoff reason", and the order check
- M8 cycle never arms: "the coordinator's cycle arms the cut-off (a new cycle end is set)"
- M9 `MARGIN_K = 0.0`: 6 failed, incl. the null control
- M10 threshold without the plan's prediction: "a room under the plan's own pre-heat + margin is not cut"
- M11 cut reason after the unmetered freeze: "the cut reason outranks the unmetered tail freeze, which this install trips"
- M12 threshold from the solve's measured start point: "a room warm at the solve is judged against the plan's predicted end, not itself"
- M13 wall-clock minimum run and stop (`as_local` for `as_utc`): "spring forward: a 7-minute true run (67 on the wall) is held by MIN_ON, not cut", "fall back: 2 true minutes to the cycle end are held by MIN_OFF, not cut"
- M14 refresh hold removed inside `allow_on`: "an early refresh inside MIN_OFF of a cut keeps the pump off", "the coordinator's cycle inside MIN_OFF of a cut does not turn the switch on"
- M17 the coordinator reads the plan's raw value instead of `allow_on`: "the coordinator's cycle inside MIN_OFF of a cut does not turn the switch on"
- M15 the hold ignores the cut-off's exemptions: "a boost set by that refresh is let through at once"
- M16 the router re-spelled as a literal `switch`: "the cut-off routes by the target's domain through pump_arbiter.switch_supply"

## Null control

- "null control: a room at or below target never cuts the pump" (18.0, 20.9, 21.0, 21.4 against 21.0): no write.
- "null control: with no cut on record allow_on returns the plan's own value", and "null control: the same cycle past MIN_OFF turns it on as the plan says" (the coordinator's own `_apply_action`).
- "NULL CONTROL: past both minimums on the transition day the warm room is cut" (the DST checks' positive arm).
- Closed loop NULL (plant = model): 0 cuts, energy and room range identical to no cut-off.
- "control: with the supply on, the same arbiter tick writes its slots", the positive control for the arbiter check. The freeze-order check asserts its own precondition: the install trips the unmetered freeze before a cut is set.

## Unpinned sites

Every site below will be pinned by `mutation-autofix` after the push (ci-autofix.md). The behaviour each one guards is already killed by a named check in the mutation proof above; the autofix only records the pins. The moved router's own site is pinned in this diff, not listed here.

- custom_components/heatpump_optimizer/coordinator.py:2416 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:122 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:139 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:164 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:167 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:171 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:190 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:193 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:193 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:195 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:201 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:207 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:209 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:211 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:213 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:215 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:217 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:224 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:224 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:231 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:238 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:238 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:250 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:250 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:255 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:258 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:263 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:263 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:265 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:265 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:267 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:272 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:274 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:274 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:283 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:283 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:283 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:288 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:292 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:295 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:298 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:298 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:301 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:301 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:303 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:85 CONST: pinned by mutation-autofix

## Figures

- Rule comparison table: `CUTOFF_ARMS=on PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/early_cutoff_closed_loop.py NULL LIGHT OWNMIN HOT SUN COLDSUN` for plan-aware; the other columns add `CUTOFF_RULE=literal` or `CUTOFF_RULE=middle`, or drop `CUTOFF_ARMS` for the no-cut-off column. The full table was measured at `7d593d589`. NULL and LIGHT were re-run at this head, with the plan-aware rule on, and printed the same figures. Harness sha1 `40195c046ba2fbedd0e17905014cb9c40fee6396`, module sha1 `1ab3fd40434339fe9ca5eb6d51bef26cf6c69391`.
- `max_class_loc` 8817 -> 8810, every other row unchanged: `python3 tests/structure.py`.
- `coord_footprint` 2587 -> 2589 and its attribution: `python3 tools/audit/archscore/score.py --diff origin/main`, attributed with `tools/audit/archscore/metrics/footprint.py`'s `coord_footprint` at the merge base and at the head.
- No closures or fast red predicted, 46 added sites: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`.
- The ledger agrees with the inventory again (only the added-sites refusal remains, which `mutation-autofix` repairs): `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --base origin/main`.
- D12-s2 surfaces: 0 failing cells at baseline, 2 under `--perturb`: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round9/D12/s2/surfaces.py --perturb`.
- The round-4 D6 register at 74 modules and 28 importers: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py`.
- Heavy suites (features, entities, DST, closures) are CI check-runs at this head, by tvofi's standing instruction.

## Red checks

At round 2's reviewed head `b731ef6b3`:
- `mutation`: MUTATION TABLE REFUSED, "the ledger disagrees with the deterministic inventory: coordinator.py:_on_off_service RETURN_DEL dac85d34". The router moved in round 1 and its pin did not. The pin is re-keyed in `3ecb86ada`. `tests/mutation_table.py --base origin/main` now prints only the added-sites refusal, which `mutation-autofix` repairs by pinning the sites listed above.
- `fast (3.14)`, `tests/entities.py`: "--anchor re-drives one site ... (R9-F10.13)" failed on the same ledger refusal. It is fixed by the same re-key, and this one check, run standalone at the head, passes.
- Cheaper detector: `tests/mutation_table.py` reads the ledger in seconds, before any mutant runs, and would have named the stale pin before the push. I did not run it in round 1. That was my omission, not a missing instrument. The D12-s2 `--perturb` arm broke without turning any check red. That gap is real: nothing runs a round's harness perturbation arms in CI. I name it here for the root-cause seat rather than build a check in this fix.
- `nightly-status`: reports main's nightly. Nothing in this diff causes it.

At round 1's reviewed head `f74924e09`, `fast (3.14)` was red on three scripts, all fixed in round 1. Each check is still named here:
- `tests/entities.py`, the migrated-module rule.
- `tests/harness_headers.py`, the D6 counts.
- `tests/layout.py`, the retired harness path.

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)

