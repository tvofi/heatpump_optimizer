A room-temperature listener, modelled on the peak guard, that switches a space-heating pump off once inside a plan interval when the room passes its threshold; the next cycle's own switch write resumes it. Decision recorded on #201 (comment 6067353918, mandate 6067089637); rule choice recorded on #201 by the orchestrator after the comparison below. Lands last in the live-fix wave, per the wave's binding design note, whose amendment A2 (the freeze order below) is already carried to fix 5.

**Shipped rule: plan-aware.** Threshold = max(active comfort target, the plan's predicted room at the end of the current step) + 0.5 K. **It was inert in every measured case and ships as a guard.** In each scenario below the 30-minute re-solve already had the pump off before the room passed the threshold. The measured overshoot goes into the floor store, which is fix 5's (the slab observer), not this one's.

Rule comparison, closed loop stepped per minute through the production listener (`tools/audit/harnesses/early_cutoff_closed_loop.py`; "warm+on" = minutes the room was above target + 0.5 K with the pump on):

| variant | no cut-off | plan-aware (ships) | literal: target + 0.5 K | middle: literal, exempt steps the plan predicts above target |
|---|---|---|---|---|
| NULL (plant = model) | 0 cuts, 2.0 kWh, room 20.11-21.02 | 0 cuts, 2.0 kWh, 20.11-21.02 | **2 cuts, 1.4 kWh, 19.99-21.00 (fails the null control)** | 0 cuts, 2.0 kWh, 20.11-21.02 |
| LIGHT (room 0.15x the model's mass, -2 degC) | 26.6 kWh, 5.82 h >21.5, max 22.60, warm+on 54 min | 0 cuts, unchanged | 5 cuts, 24.0 kWh, 0.00 h >21.5, max 21.11 | 0 cuts, unchanged |
| OWNMIN (the finder's pump >= 3 kW) | 2.5 kWh, max 21.06 | 0 cuts, unchanged | not run | 0 cuts, unchanged |
| HOT (>= 6 kW, COP 1.4x) | 3.0 kWh, max 21.43 | 0 cuts, unchanged | not run | 0 cuts, unchanged |
| SUN (600 W/m2 unforecast, 12 degC) | 2.0 kWh, 12.70 h >21.5, warm+on 0 min | 0 cuts, unchanged | not run | 0 cuts, unchanged |
| COLDSUN (same sun, -2 degC) | 18.4 kWh, 10.77 h >21.5, warm+on 0 min | 0 cuts, unchanged | not run | 0 cuts, unchanged |

The literal rule acts on LIGHT but cuts a correct plan's night-to-day pre-heat on NULL (threshold 20.0 at the 19.5 night target), so it does not ship. The middle rule passes NULL but does not act on LIGHT, so by the recorded decision plan-aware ships.

What the cut-off does and leaves alone (`custom_components/heatpump_optimizer/early_cutoff.py`):
- Takes `ArbiterInputs` values, the boost record and the optimizer config; only `state_for` keys on the coordinator (design note rule A).
- Short cycles: no cut on a pump on for under 10 min (`MIN_ON`; a missing or future switch stamp is an unknown run), none with under 10 min to the next cycle (`MIN_OFF`), at most one per cycle. The integration had no minimum on/off time of its own. UTC arithmetic (the DST suite caught a wall-clock version).
- Acts only on a `step_duty == "space"` step. Exempt: hot-water, both and idle steps, a boost on either channel, disinfection, a running defrost, a tank below its minimum, non-plan modes, a stale plan, a cold lower zone. Writes only the power switch; the arbiter writes nothing while the switch reads off, so it cannot re-enable within the cycle (checked, with a positive control). ECL110 displacement and the peak guard keep their own writers.
- Margin is a constant 0.5 K: an options field would move `tests/golden/config_flow.json`, which only a claim can, and add a string to both translation files.
- Learners: a cut interval freezes them under one reason, `early_cutoff`, held for the cut cycle and the next. **Order: the cut reason is returned by `_tail_freeze` before the unmetered-power freeze** (design note A2: the slab observer ignores only the unmetered reason). A check fails if the order is reversed (mutant M11).
- Diagnostics: the `(key, view)` loop in `diagnostics.py` (design note S7), row `early_cutoff`: margin, minimum times, `cut_this_cycle`, `interval_cut`, count, the last cut (time, room, threshold, switch) and `last_held`. Each cut logs at INFO.

Structure: every row in `tests/structure_budgets.json` is unchanged; no raise. The coordinator class gains the two-line arm and loses the freeze lines (moved into `_tail_freeze`, where A2's order is local to one function) and two step labels made false by the steps now preceding them.

## Head

`007d44db34206df59e62b97d373b2369c5a64d94`: the authored commit `b3ecf8be9`, two merges of origin/main (`4dbe5aace`, then `bd59a4af1`) and one commit adding `early_cutoff.py` to the 21 recorded closures that list `coordinator.py` or `diagnostics.py`, which import it at module level (as #1745 did for `entry_config.py`). Figures measured 2026-10-08T23:03Z at `7d593d589`; the later commits change no production line.

## Mutation proof

Each mutant applied to the head and the new feature section driven (`tests/features.py`, section "early cut-off"); every one turns at least one check red. M0 (no change): 0 failed.

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

## Null control

- `null control: a room at or below target never cuts the pump` (18.0, 20.9, 21.0, 21.4 against 21.0): no write.
- Closed loop NULL (plant = model): 0 cuts, energy and room range identical to no cut-off (table above).
- "control: with the supply on, the same arbiter tick writes its slots" is the positive control for the arbiter check.
- The freeze-order check asserts its precondition: the install trips the unmetered freeze (`_tail_freeze` non-None) before a cut is set.

## Unpinned sites

Every site below: pinned by `mutation-autofix` after the push (ci-autofix.md). The behaviour each guards is already killed by a named check in the mutation proof above; the autofix records the pins.

- custom_components/heatpump_optimizer/coordinator.py:2427 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:91 CONST: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:124 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:142 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:145 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:167 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:170 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:185 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:191 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:193 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:195 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:197 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:199 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:201 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:208 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:208 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:215 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:222 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:222 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:234 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:234 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:239 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:242 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:247 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:247 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:249 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:249 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:251 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:256 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:258 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:258 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:267 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:267 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:267 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:272 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:276 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:279 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:282 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:282 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:285 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:285 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/early_cutoff.py:287 GUARD_OFF: pinned by mutation-autofix

## Figures

- Rule comparison table: `CUTOFF_ARMS=on PYTHONPATH=tests/hastub:custom_components:tests python3 tools/audit/harnesses/early_cutoff_closed_loop.py NULL LIGHT OWNMIN HOT SUN COLDSUN` (plan-aware); with `CUTOFF_RULE=literal` / `CUTOFF_RULE=middle` for the other columns; without `CUTOFF_ARMS` for the no-cut-off column. Harness sha1 `0bdfce9803f681f25e5eb7c516ae44dd6ee4a6ad`, module sha1 `d89ad2b793e8ec2c2fbf5c1c662133970d5519d9`.
- Structure rows unchanged: `python3 tests/structure.py`.
- Architecture score (report-only): `python3 tools/audit/archscore/score.py --diff origin/main`.
- Feature checks, DST suite, entities and closures: CI check-runs at this head (heavy suites left to CI by tvofi's standing instruction).

## Red checks

none. The new module's closure entries are in this diff, so `tools/pr/ci_predict.py` predicts no `closures` or `fast` red.

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
