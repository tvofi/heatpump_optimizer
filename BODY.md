R10-WATER-SETPOINT-FEEDBACK part 3: the two clamp-bound reads of `Carry 8` (https://github.com/tvofi/heatpump_optimizer/pull/3372#issuecomment-6756915104), as the orchestrator narrowed it on 2026-11-11T06:30Z — the controller's lower and upper limit on the written set-point (inputs 10104 and 10103 of the reporting controller) as two optional entity options. Input 10107 is not read here; it is built once, by R10-OUTSIDE-DHW-START-HYSTERESIS.

This head answers `Fix review: blocked 6f1dd2040ce51f5dbff0ce67ffc1085637b29ea6 class-open`: a high-limit sensor reading at or below the gate made the loop write the gate or below it. The class, not the instance, is closed in `pump_arbiter._feedback_bounds`.

The defect. `_feedback_bounds` took the sensor's reading as the loop's upper bound unconditionally, and `_feedback` and `inputs.quantise_setpoint_c` both let an upper bound win over a lower one, so a reading under the loop's gate clearance became the write: 15.0 °C against a 20.0 °C gate, the gate itself for a reading at it, and the gate again for a reading between it and the entity's next step (rounded down onto it).

The bound, and its physical reason. The gate is the value a step that does not heat writes (`_gate_c`): to the controller it means off. A heating write must therefore sit at least one entity step above it, which is the loop's lowest write (I2, `FEEDBACK_GATE_CLEAR_K`). A controller upper limit under that value leaves no heating value inside it, so it cannot be the upper limit of a heating set-point: it is a sensor in the wrong slot, a placeholder, or a parked circuit. `_feedback_bounds` now keeps a controller's upper limit only where it is at or above the gate plus one entity step, computed by the same `_bounded` call that rounds the loop's own lowest write; a lower one is left out exactly as an unavailable or implausible one is, and the loop is bounded by the ceiling and the readback cut as with no sensor. The same rule is applied to the readback cut `FeedbackRun.cut_hi_c`, the sensor's one sibling in the upper bound that also comes from the controller.

A reading that is unavailable, not a number or implausible was already `None` (`_setpoint_limits_c`); neither key has an age limit, so a 30-day-old reading at the gate is read and left out by the new rule, and under an age limit (mutant O3 below) it is stale and left out by the reader.

What the whole diff builds (parts unchanged since the reviewed head are restated because the body is re-taken whole):

- `space_setpoint_low_limit_entity` and `space_setpoint_high_limit_entity` (`const.py`), two temperature-sensor pickers on the options page that carries the space set-point unit, shown for a water unit (`config_flow._OPTION_FIELDS`, `when=_water_space_setpoint`), with labels in `strings.json`, each translation and the card, a `WATER_RANGE_C` row each in `const.INPUT_PLAUSIBLE_RANGE_C`, and their place in `_ABSENT_IS_NOT_DEFAULT`.
- `pump_arbiter._setpoint_limits_c` reads both through `InputReader` and `_feedback_bounds` joins them to the loop's bounds. `_clamp_cut` stays for an install that names neither sensor.
- Absent, never guessed: an unset, unavailable, non-numeric or implausible sensor, a pair that is not lower below upper, and now an upper limit under the lowest heating write.
- The limits bound the loop alone (I1, I3): the first write of a run and every non-qualifying pass are today's open-loop target.

Alternatives for this round (fixer.md step 17):

- Raise the upper bound to the gate clearance instead of leaving the limit out (`hi = max(hi, lowest)`). Lost: it pins the loop one step above the gate on the word of a reading already shown not to be a heating limit, far below the inlet, which stops the compressor; leaving it out returns the loop to the ceiling and the readback, which is what an unreadable sensor does.
- Reject the reading in `_setpoint_limits_c` only. Lost: the readback cut reaches the same `min` and would stay open; one filter in `_feedback_bounds` covers both controller-reported uppers.
- A fixed margin above the gate (the minimum lift, 0.5 K). Lost: a literal with no measurement behind it; the entity's own step is the smallest bound that makes a write at the gate impossible, and it is the loop's existing lowest write.
- Clamp the final write above the gate after `_bounded`. Lost: it hides which bound was wrong and keeps a bad limit as the loop's target.

## Head

`580f12908056021e9448d5f0520919044e6de41a`, measured against `origin/main` `50e4b1aa259827e0c74366bc45d065c26e3cc86c` on 2026-11-11 (UTC); `git merge-tree --write-tree origin/main HEAD` prints one tree and no conflict. It adds four commits to `c9f324c7bd9d256cb319c15ed0bc5b3c3206af75`: the failing test and harness rows, the fix with its docs sentence, the sibling-path checks, and one ledger file removed.

## Mutation proof

Each mutant is one edit in a `git archive` copy of the head (M1–M3: a copy of the working tree at the fix commit), run with `PYTHONPATH=tests/hastub python3 tests/features.py`. Every copy also fails `and the path that proceeds still stamps a resolvable recorded_at (#363)`, the copy's and not the mutant's, and main's `combi_type_branch census` (see Red checks); neither is counted below.

This round's fix, in `_feedback_bounds`:

- M1, `and v >= lowest` deleted from the filter: FAIL the three checks `part 3 I2: a high-limit sensor reading below the gate, at it or just above it ...`, `part 3 I2: a high limit under the lowest heating write ...` and `part 3 I2: no controller upper limit, read from its sensor, from a readback cut or from both ...`.
- M2, `v >= lowest` to `v > gate` (the instance alone, without the step): FAIL the same three.
- M3, `lowest = clear` (no rounding to the entity's step): FAIL the same three.

The earlier rounds' mutants, re-run at this head:

- O1, `lows.append(low)` deleted: FAIL `part 3, minimum return target 28.0 degC read from its sensor: no write goes below it and the controller cuts nothing`.
- O2, `high` dropped from the filtered uppers: FAIL `part 3, return limit 27.6 degC read from its sensor ...`, `part 3 I2: a high limit under the lowest heating write ...`, `part 3 I1 null control: the same 24.0 degC limit moves the loop's own writes ...` and `part 3 I2 null control: the same pass with a limit well above the gate returns that limit ...`.
- O3, both keys given a 30-minute entry in `const.INPUT_MAX_AGE_MINUTES`: FAIL `part 3: a limit last reported 30 days ago still bounds the loop` and the age table's two censuses (`every age-limited key declares its on-change limit ...`, `all 30 age-limited keys: ...`).
- O4, the crossed-pair test replaced by `if False:`; O5, `low >= high` to `low > high`; O6, both `WATER_RANGE_C` rows deleted: each FAIL `part 3: an unavailable, non-numeric or implausible limit sensor, and a crossed or equal pair, write exactly what no limit sensor writes`.
- O7, `reading.value if reading.ok else None` to `reading.value`: not re-run; equivalent by the reader's contract as before (a reading that is not `ok` carries no value while neither key has an age limit).

Failing test first: at the commit `features, harness: no controller upper limit brings a loop write to the gate (failing test)`, the parent of the fix commit — `tests/features.py` fails exactly the three I2 checks named under M1 beside main's census, with `lowest write` 15.0, 19.9 and 20.0 against the 20.0 gate on a return target and 20.0, 24.9 and 25.0 against 25.0 on a flow target, and the grid check reporting 2304 of its 3024 passes at or below the gate.

## Null control

- With no limit sensor the lowest write is above the gate on both units (`part 3 I2 null control: with no limit sensor the lowest write is above the gate too`), at both ends: a write at the gate is the sensor's doing, not the fixture's.
- The grid reaches the upper bound: `part 3 I2 null control: the same pass with a limit well above the gate returns that limit` (24.0 returned for a 24.0 limit under a 30.0 target); had the grid's passes never touched the bound, the grid check would pass on any tree. Mutant O2 turns it red.
- A limit one step above the gate is still used, not discarded with the rest: the `+0.1`, `+0.15` and `+0.3` cells of `part 3 I2: a high limit under the lowest heating write ...` must differ from the no-sensor writes, and the cells under one step must equal them, in one check.
- Sibling paths: `part 3 I1: the indoor target, an unmetered or switched-off loop, a step that does not heat and the start hold ...` compares full write lists under a 24.0, a 20.0 and a 15.0 °C high limit with no sensor, each list non-empty; its null control is the loop itself, which the same 24.0 °C limit moves (`part 3 I1 null control`).
- The unmodified tree: the group harness at `c9f324c7b` prints `above the gate False` on six of its ten gate rows; at the head all ten print `True`, and its seven earlier rows are byte-identical at both ends.
- Flat-price null control: not applicable, the plan and the planner are untouched and no cost figure is claimed.

## Figures

- Harness at both ends, `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_water_setpoint_feedback.py` (the head's file, sha1 `b020240632b24ddc9d10df19d1535baa603cf36a`, run against the production tree of `c9f324c7b` and of the head): the rows `return gate 20.0 high limit 15.00`, `20.00`, `20.05` and `flow gate 25.0 high limit 20.00`, `25.00`, `25.05` print `lowest` 15.0, 20.0, 20.0, 20.0, 25.0, 25.0 and `above the gate False` before, and `lowest 26.0 above the gate True` with the no-sensor row's write count after; the `unset` and `+0.10` rows and the seven rows above them do not move.
- Grid size: 3024 loop passes, the product the check itself asserts (2 units, 3 entity steps, 3 sources, 14 limit offsets from 8 K under the gate to 2 K over it, 4 targets, 3 inlets); 22 simulated three-hour blocks in the sensor check (2 units, 11 offsets and one 30-day-old reading each).
- Seams, readers of the two sensors, rule `git grep -n "_setpoint_limits_c(\|SETPOINT_LIMIT_KEYS\|SPACE_SETPOINT_\(LOW\|HIGH\)_LIMIT_ENTITY" -- 'custom_components/*.py'`: outside imports, definitions, the options rows of `config_flow.py` and the plausibility rows of `const.py`, one call, in `_feedback_bounds`. Closed in this diff.
- Seams, producers of a space set-point value, rule `git grep -n '_bounded(inp, "space_setpoint"\|"space_setpoint",$' -- custom_components/heatpump_optimizer/pump_arbiter.py`, by function: `_feedback` (the loop's write, the only one fed by `_feedback_bounds`: closed in this diff); `_feedback_bounds` (the new probe of the lowest heating write, not a write); `_space_target` (the indoor target), `_flow_target` (today's heating target and the fallback hold), `_gate_c` (the gate of a step that does not heat) and `desired` (the indoor hot-water fallback): none reads a limit sensor, pinned by the sibling check above, already guarded; `_flow_command` (a ceiling for `draw_range`, not a write).
- Seams, the uppers inside `_feedback_bounds`: the sensor (closed), the readback cut `cut_hi_c` (closed by the same filter, driven by the grid's `cut` and `both` sources), and the configured ceiling. The ceiling is the user's and is not filtered: where it sits at or under the set-point entity's own minimum the loop returns the gate or below it, and so does today's open-loop target with the same value (probe: entity minimum 30, ceiling 28.0 and 30.0, both units, `_flow_target` and `_feedback` return the same 28.0 and 30.0 against a 30.0 gate). That value is `_flow_target`'s on `origin/main`, written with the loop off and with no limit sensor alike, so it is outside this class (a controller-reported upper limit reaching the gate) and already guarded to the extent `_heat_ceiling_c` guards it: a ceiling at or under the fixed 25 °C gate reads as the default, and the options flow offers none under 30 °C. No install with a set-point minimum above its ceiling is measured; nothing here constrains a later stage, so it is recorded and not carried.
- The lower side: a low-limit reading only raises the lower bound, which already holds the gate clearance, so no reading of it lowers a write; O1 and the `part 3, minimum return target` check cover its use.
- Architecture score: `python3 tools/audit/archscore/score.py --diff origin/main` printed `Architecture score: dS +0.0000 NULL`.
- Structure ratchet: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed a `MODE: SCOPED` line; `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at the head ran every script its scope names, `tests/stress.py` included, and printed `1 TEST SCRIPT(S) FAILED`: `tests/features.py`, on main's combi census check alone (`1 of 5252 FEATURE CHECKS FAILED`).
- Closures: `tools/pr/prepr.sh` ran with `PREPR_SKIP_CLOSURES=1`, the ruled allowance for an interpreter without `homeassistant` (`python3 -c 'import homeassistant'` raises `ModuleNotFoundError` here); without it the step refused on `tests/features.py (exit 1)`, the census red above, and its `ci predict` step printed no closures, fast, governance or instrument red predicted.
- Goldens: the same run's `tests/env_drift.py --all origin/main` printed `is byte-identical to origin/main here` for every fixture it lists, `config_flow` among them; both claim files are untouched.
- Combi census (`tests/features.py`, check `combi_type_branch census`): at the head it lists six lines, `const.py:812`, `const.py:1603`, `heat_curve.py:72`, `pump_arbiter.py:258`, `pump_arbiter.py:1058`, `thermal_model.py:1870`; none is the two this branch had added (`config_flow.py:1704`, `const.py:836`), and `git show origin/main:custom_components/heatpump_optimizer/pump_arbiter.py | grep -c` of the vendor name prints the same two `pump_arbiter.py` lines main carries.

## Unpinned sites

- `tests/mutation_ledger/killed_by/pump_arbiter.py/_feedback_bounds.RETURN_DEL.1af408a4.json` is removed: it pins the old text of `_feedback_bounds`' return line, which this diff rewrites, and `python3 tests/mutation_table.py --pin-killed --base origin/main` refused with `disposition names no site the inventory generates` while it stayed.
- The three sites the diff adds are not pinned in the ledger: the same command, re-run after the removal, printed `MUTATION TABLE INCONCLUSIVE` — `the baseline is already red in tests/features.py`, on main's combi census lines — so it recorded no driver verdict; the rows are `mutation-autofix`'s once main's census is green (PR #3466). Each operator's own mutant was run by hand in a `git archive` copy of the head with `PYTHONPATH=tests/hastub python3 tests/features.py`:
- custom_components/heatpump_optimizer/pump_arbiter.py:993 BOOLOP: killed by `tests/features.py` (`and` to `or`: the script stops on `TypeError: '>=' not supported between instances of 'NoneType' and 'float'`).
- custom_components/heatpump_optimizer/pump_arbiter.py:993 CMP_BOUND: killed by `tests/features.py` (`>=` to `>`: FAIL `part 3 I2: a high limit under the lowest heating write ...`, its `+0.1` cells).
- custom_components/heatpump_optimizer/pump_arbiter.py:994 RETURN_DEL: killed by `tests/features.py` (`pass`: the script stops on `TypeError: cannot unpack non-iterable NoneType object`).
- The three `_setpoint_limits_c` pins of the reviewed head are untouched and that function's text is unchanged.

## Red checks

- `tests / fast (3.14)`: red on main's own six vendor-name lines listed under Figures, which PR #3466 repairs; the two lines this branch had added were reworded in `c9f324c7b` and are not among them. No cheaper detector is owed by this branch for main's lines.
- `tests / mutation`: predicted red or inconclusive for the same cause (the census turns `tests/features.py`'s baseline red, see Unpinned sites). The cheaper detector exists and ran: `mutation_table.py --pin-killed` locally, which reported it before the handoff.
- `governance / instrument-self-tests`: main's (R10-HOTFIX-PUSHER-CENSUS), not in this branch's diff.

## Forward-carry

none

## Friction

none
