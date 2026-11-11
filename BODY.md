R10-WATER-SETPOINT-FEEDBACK part 3: the two clamp-bound reads of `Carry 8` (https://github.com/tvofi/heatpump_optimizer/pull/3372#issuecomment-6756915104), as the orchestrator narrowed it on 2026-11-11T06:30Z — the controller's lower and upper limit on the written set-point (a Luxtronik's inputs 10104 and 10103) as two optional entity options. Input 10107 is not read here; it is built once, by R10-OUTSIDE-DHW-START-HYSTERESIS.

What the diff builds:

- `space_setpoint_low_limit_entity` and `space_setpoint_high_limit_entity` (`const.py`), two temperature-sensor pickers on the options page that carries the space set-point unit, shown for a water unit like the lift, the ceiling and the loop's own option (`config_flow._OPTION_FIELDS`, `when=_water_space_setpoint`). R10-OUTSIDE-DHW-START-HYSTERESIS reuses this plumbing for its start-condition option: one `_F` row with `_STORED` and `_entity_of('sensor', 'temperature')`, a label and description in `strings.json` and each translation, a `health.input_<key>` label per language in the card, a `WATER_RANGE_C` row in `const.INPUT_PLAUSIBLE_RANGE_C`, and the key's place in `_ABSENT_IS_NOT_DEFAULT`.
- `pump_arbiter._setpoint_limits_c` reads both through `InputReader` and `_feedback_bounds` joins them to the loop's bounds, so a loop target never passes a limit and no write is cut. `_clamp_cut` stays: an install that names neither sensor, and a controller that publishes none, is still cut and adopted as before.
- Absent, never guessed: an unset, unavailable, non-numeric or implausible sensor is left out, and a pair that is not lower below upper (two sensors in each other's slot) is left out whole. Neither key has an age limit: a limit is a setting whose sensor reports on change (the contributor: read every 10th poll), so only `unavailable` says the source is gone.
- The limits bound the loop alone. Today's open-loop target (the first write of a run, the start hold, every non-qualifying pass) is not moved by them, which keeps the design's I1 and I3: a first write past a limit is cut and raises today's repair, with or without the sensors.

Unset, every write is what `origin/main` writes: the `features.py` section replays an indoor unit, an install without a power entity and one with the option off with both sensors against neither, and the group harness prints its three part-1 rows unchanged.

The contributor is asked, not waited on: with *Temperature: return target minimum* and *Temperature: return limit* of ha-luxtronik-shi selected in the two new fields, a heating block that drives the loop to either limit should show no written value outside [10104, 10103] in the set-point's history, and the readback (input 10101) equal to each write.

Where each carry of the group stands at this head:

- Carry 1 (the trailer): the three code commits of this branch carry `Co-authored-by: Bankaifan`; parts 1 and 2 merged as #3405 and #3433.
- Carry 2 (start-then-hold, anchor once): `FEEDBACK_START_HOLD` and the deadband hold in `pump_arbiter._nudged`, from #3405.
- Carry 3 (F1–F6): F1 `_clamp_cut` and, from this diff, `_setpoint_limits_c`; F2 and F4 the preconditions in `docs/configuration.md` under Pump duty control and the run reset in `_clamp_cut`'s caller `hold`; F3 `FEEDBACK_DEADBAND_SHARE` (kW, no kelvin deadband); F5 the docs line on a second writer; F6 `FEEDBACK_START_HOLD`. All from #3405.
- Carry 4 (owner decision, option default on): `CONF_SPACE_SETPOINT_POWER_FEEDBACK` with `DEFAULT_SPACE_SETPOINT_POWER_FEEDBACK`, a conjunct of `_feedback_on`, from #3405.
- Carry 5 (design round 2, R1–R5): `_clamp_cut`, `_note_stop`, `FEEDBACK_DOWN_K`, and the fixture repeats in the `features.py` section, from #3405.
- Carry 6: dismissed on the roster as a duplicate of Carry 7.
- Carry 7 (one write record): the loop writes `ArbiterState.written["space_setpoint"]` in `_note_sent` and `_clamp_cut` and adds no second record, from #3405.
- Carry 8: the watchdog, polling and 0.5 K statements from #3433; the 10104 and 10103 reads from this diff; the 10107 read with R10-OUTSIDE-DHW-START-HYSTERESIS by the orchestrator's ruling.

Alternatives (fixer.md step 17):

- Clamp every space water write to the read limits, the first write of a run included. Lost: it departs from the approved note's I3 (the first write is today's) and would silence today's repair for a set-point the controller cannot hold; a departure is raised, not made. So a first write of a run past a read limit is still cut and still raises the repair (`part 3 I3` pins it); no install it bites is measured, and whether to clamp it is the owner's or the orchestrator's.
- Derive the two sensors' entity ids from the set-point entity's id (the `modbus_prefill.package_prefix` shape). Lost: the ids belong to a third-party integration this repository does not control, and a guessed id that resolves to another sensor is a guessed limit.
- An explicit no-age-limit override at the read. Lost: a key absent from `const.INPUT_MAX_AGE_MINUTES` already has none, so the override stated the table's rule a second time and no test separated the two (mutant M3 survived it).
- Replace `_clamp_cut` by the reads. Lost: a controller without the sensors still needs the inference.

## Head

`100ff9351df307cbdaaea4c24ae15cb78ff1c799`

## Mutation proof

Each mutant applied to a detached worktree of `1881627d19` (the head's parent; the head adds ledger files only), `PYTHONPATH=tests/hastub python3 tests/features.py`, failing check names below; the unmutated tree there exits 0 with no `FAIL` line.

- M1, `lows.append(low)` deleted in `_feedback_bounds`: FAIL `R10-WATER-SETPOINT-FEEDBACK part 3, minimum return target 28.0 degC read from its sensor: no write goes below it and the controller cuts nothing`.
- M2, `high` dropped from `highs` in `_feedback_bounds`: FAIL `R10-WATER-SETPOINT-FEEDBACK part 3, return limit 27.6 degC read from its sensor: no write passes it, so the controller cuts nothing, and no repair is raised`.
- M3, both keys given a 30-minute entry in `const.INPUT_MAX_AGE_MINUTES`: FAIL `R10-WATER-SETPOINT-FEEDBACK part 3: a limit last reported 30 days ago still bounds the loop`, and the age table's own two censuses (`every age-limited key declares its on-change limit ...`, `all 30 age-limited keys: ...`).
- M4, the crossed-pair test replaced by `if False:`: FAIL `R10-WATER-SETPOINT-FEEDBACK part 3: an unavailable, non-numeric or implausible limit sensor, and a crossed or equal pair, write exactly what no limit sensor writes`.
- M5, `low >= high` to `low > high`: FAIL the same check (its `equal` cell).
- M6, both `WATER_RANGE_C` rows deleted from `const.INPUT_PLAUSIBLE_RANGE_C`: FAIL the unusable-sensor check named under M4 (its two `fault code` cells).
- M7, `reading.value if reading.ok else None` to `reading.value` in `_setpoint_limits_c`: survives, equivalent: with no age limit on either key a reading that is not `ok` has no value (`InputReader.read` sets `value` only past `_begin`, and withdraws it when implausible), so the guard changes no output; it is kept because `ok` is the reader's contract and M3's world (a stale reading keeps its value) is one table row away.

Failing test first: at `6e7536b70d` (the section alone on `f24d107bd7`) `tests/features.py` exited 1 on exactly the two sensor checks named under M1 and M2, with `highest write 28.1, cut 27.6` and `lowest write 27.6, cut 28.0`.

## Null control

- The unmodified tree: the two failing checks above, and the group harness `dev/audit/harnesses/r10_water_setpoint_feedback.py` printing each `sensor set` row equal to its `sensor unset` row at `6e7536b70d` (the keys are read by nothing), where the head prints 27.6 against 28.1 and 28.0 against 27.6.
- The fixture moves without the sensors: `part 3 null control: the same block with no limit sensor writes past 27.6 degC before the cut is read back` and `... writes below 28.0 degC and is cut there` pass at both ends; had the block never reached a limit, the sensor checks would pass on any tree.
- Unset is byte-identical: the harness's three part-1 rows are the same at `6e7536b70d` and the head, and `part 3 I1: an indoor unit, no power entity or the option off writes the same with both limit sensors as with neither` compares full write lists; the unusable-sensor check requires more than 10 writes in the list it compares, so an empty replay cannot pass it.
- Flat-price null control: not applicable, the plan and the planner are untouched (the design's I5) and no cost figure is claimed.

## Figures

- Harness at both ends, `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_water_setpoint_feedback.py` (the head's file, sha1 `ee9f738ce477dddab30d808eef4cdaddcdbbf178`, run against each tree): at `6e7536b70d` the rows `return limit 27.6 sensor unset` and `sensor set` both print `highest 28.1`, and `return minimum 28.0` both print `lowest 27.6`; at the head `sensor set` prints `highest 27.6` and `lowest 28.0`. The three part-1 rows are identical at both ends.
- Seams that bound a space set-point write, rule `git grep -n -E '_bounded\(inp, "space_setpoint"' -- 'custom_components/*.py'`, five sites: the loop's write in `_feedback` (closed in this diff: its `lo` and `hi` carry the read limits); the indoor target in `_space_target` (not a water set-point, the limits do not apply); the gate write in `_gate_c`'s caller and the frost value in `release` (must reach the controller's off value, already guarded by the entity's own range); today's open-loop target in `_flow_target` (left as it is by I3, see Alternatives).
- Options plumbing, rule `git grep -c -E 'space_setpoint_(low|high)_limit_entity' <ref> -- custom_components docs`: no line at `origin/main` (exit 1), seven files at the head.
- Architecture score: `python3 tools/audit/archscore/score.py --diff origin/main` printed `Architecture score: dS +0.0000 NULL`.
- Structure ratchet: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed a `MODE: SCOPED` line; every script its `scope.run` names exits 0 at the head except `tests/stress.py`, left to CI.
- Goldens: `GOLDEN_MODE=drift python3 tests/golden.py` exits 0 and prints `config_flow is byte-identical to origin/main here` (the two rows render only for a water unit); both claim files are untouched.

## Unpinned sites

`python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3` ran at `1881627d19`, the parent of the head, which adds only the three ledger files it wrote; it printed `PIN KILLED: 3 pinned, 0 left unpinned`.

- custom_components/heatpump_optimizer/pump_arbiter.py:1001 CMP_BOUND: pinned, killed by `tests/features.py` (hand mutant M5).
- custom_components/heatpump_optimizer/pump_arbiter.py:1001 GUARD_OFF: pinned, killed by `tests/features.py` (hand mutant M4).
- custom_components/heatpump_optimizer/pump_arbiter.py:1003 RETURN_DEL: pinned, killed by `tests/typing_ruler.py`.
- `_setpoint_limits_c`'s `reading.ok` guard is no site of the ledger's operators; hand mutant M7 above is its disposition (equivalent).

## Red checks

none

## Forward-carry

none

## Friction

none
