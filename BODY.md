Closes #3786

R11-SEAM-wallclock-dst (class P7 residual). Four production seams carried a wall-clock hour across a DST change as if every day had 24 h:

- `ThermalModel.simulate_trajectory`, `simulate_trajectory_batch` and `simulate_trajectory_with_dhw` derived each step's hour of day as `start_hour + i * dt_hours`. On a transition day, from the change onward, every step read the learned internal-gains profile (and, for the DHW twin, the draw pattern) an hour off the step clock the optimizer builds (`optimizer._step_clock`, walked in UTC by `drift.utc_step_starts`). They now take that clock as `step_hours` and do no clock arithmetic of their own. Every production caller already held it (`h.step_hours`); `_optimize_with_dhw` no longer recomputes `start_time.hour + start_time.minute / 60`. With no clock, `simulate_trajectory_with_dhw` keeps its former default, a zoneless day from midnight.
- `dhw_schedule.hours_until_next_window` returned the wall-clock gap as a duration, which is 3.5 h from 00:30 to a 04:00 window when the spring-forward day holds 2.5 real hours. It now takes the aware `now` and returns the real time to the first instant after `now` at which the zone's wall clock enters a window of today's or tomorrow's schedule (`_window_entries`). The clock enters a window in two ways. One is the window's start, read at every instant that wall time occurs: once, twice in an autumn repeated hour (fold 0 and fold 1, each kept only where it round-trips), never in a spring skipped hour. The other is a DST jump (`_offset_change`, the day's offset change found to the second) that lands inside a window the clock was outside the second before (`_wall_inside`). The gap is measured with `drift.utc_elapsed_seconds`, which reads a naive instant through the kernel-step definition `drift.utc_instant`. Its three callers pass an instant: the coordinator's published countdown (`dt_util.now()`), the VVC pre-heat lead (`pump_schedule.vvc_should_run`, now taking `now`), and the planner's `next_window_in_hours`. The planner passes `h.start_time`, which its horizon protocol now declares.

The brief places the naive-instant definition "in const". Kernel-step landed it as `drift.utc_instant` (#3728), and this diff reads it there.

The brief's three instances are fixed, plus `simulate_trajectory_with_dhw`, which the issue's sweep lists (three times) and the brief omits. D15-s2-04 (unreproduced at judging) is recorded and not edited: its harness (`m5_zone.py --bundle B`) needs a diagnostics bundle the tree does not carry, and the register records `debug_replay.py` with 0 occurrences of `HASTUB_TZ`.

## Head

`dc3d55e2e6b54eb1a144c7588adee3df3a735c45`, measured on origin/main `8890fc2bada17f6c7d8a6bbf03e6625a16a0967c` (merge base `46d0a521befa01ff62cf647e04d3a2b783ea2fc1`), 2026-11-27T01:00:03Z. It is the reviewed head `411932cae18926136f04692026a5be881b4c6e70` plus three commits answering verdict `91efc5be1f`. `git merge-tree --write-tree origin/main HEAD` exits 0 (`LEDGER-MERGE: resolved tests/closures.json`).

## Verdict response

Round 2, answering `Fix review: blocked 411932cae1 class-open` (refs/heads/verdict/3914).

- Block, the autumn repeated hour (fold=1 `now` at 02:30, a 02:45 window returned -0.75 h). The reviewed head built the opening with `datetime.combine(..., now.tzinfo)`, always fold 0. The opening is now each instant at which the start's wall time occurs, and the first one after `now` counts. From 02:30+01:00 the 02:45 window reads 0.25 h, and `vvc_should_run` pre-heats in both passes. The new checks are `the next-window countdown runs to the first instant the wall clock enters a window: ...` and `the circulation pump pre-heats 15 min before a 02:45 window from 02:30 in either pass of the autumn repeated hour, as on a plain day`, both with the plain day as the null, as the verdict asked.
- The axis, not only its member (ADDENDUM rule 8). The set the claim quantifies over is every `now` against every window start on a transition day. Its members fall under three ways a zone maps a wall start onto instants: once, twice (fold) or never (gap). There is also a fourth way the clock enters a window without reading its start: a jump that lands inside one. The rule enumerating the set is the harness's new `next_window_census` instance, defined below. At the reviewed head it reads 76 autumn and 136 spring cells off the zone's clock. Beyond the verdict's member, those cells hold three more members of the same axis. (a) In the first pass of the repeated hour, a start earlier in that hour (from 02:30, 02:15) recurs in the second pass, 0.75 h on, where the head read 24.75 h. (b) The fall-back jump lands inside a window whose start passed (01:30-02:15 from 02:30 fold 0): it opens at the jump, 0.5 h on. (c) A start in the spring skipped hour opens at the jump when the window reaches past it (02:30-04:00 from 00:30: 1.5 h, the head read 2.0 h). It never opens that day when the jump skips the window whole (02:15-02:24: 24.75 h). All four read 0 cells at this head.
- Note, stale `## Raise justification`. Removed. The three-dot diff moves `tests/structure_budgets.json` only down (`class_excess_loc` 17220 -> 17209, `module_excess_loc` 21646 -> 21639; `name_kept_members` stays 38), the payment being `3e618a5f60`'s removal of the unread `OpenMeteoSolar.observed`. This head raises no budget, so the `budget-raise-gate` entry is gone from `## Red checks`.

## Mutation proof

Each mutant was applied alone to `dhw_schedule.py` at this head and restored (`cmp` against the saved fix read identical). Each run uses `tools/audit/seat/features_block.py` from `# P7, issue 3786: a wall-clock hour` to `def _p7_slips(name, day):`, with the block's emitted prelude, plus `next_window_census --day spring|autumn`:

- M0, `dhw_schedule.py` back to the reviewed head `411932c` (the repair removed): FAIL `the next-window countdown runs to the first instant the wall clock enters a window: ...` and FAIL `the circulation pump pre-heats 15 min before a 02:45 window from 02:30 in either pass ...`; census spring 136, autumn 76 of the cells off.
- M1, the start's fold loop `(0, 1)` to `(0,)`: the same two checks FAIL; census spring 0, autumn 47.
- M2, `out.append(jump)` deleted: the countdown check FAILS; census spring 80, autumn 19.
- M3, the round-trip guard `if instant.astimezone(zone).replace(tzinfo=None) == wall.replace(tzinfo=None):` to `if True:`: the countdown check FAILS; census spring 156, autumn 0.

Earlier rounds' proofs for the trajectory seams stand on unchanged lines (`thermal_model.py`, this diff's earlier commits). The restoration of `thermal_model.py` scalar `float(gains_clock[i]) % 24.0` to `(step_hours[0] + i * dt_hours) % 24.0` fails `every trajectory step reads its gains and draw hour off the step clock on both DST days and a plain one (scalar, batched, with hot water)`. This pass re-ran none of those per mutant.

`tests/dst_checks.py`, the wall-clock tracer (round-9 P7 barrier), under `HASTUB_TZ=Europe/Stockholm` at this head: `ALL 137 DST / QUARTER-GRID CHECKS PASSED`. The new route walks no zoned stamp with `+ timedelta`. Every step is a `datetime.combine` or a UTC instant.

## Null control

The plain day (2026-06-10) is each arm's null control. `next_window_census --day plain` reads 0 cells off at the merge base, at the reviewed head and at this head. Had the census oracle disagreed with the function on ordinary days, it would have read off there. In the new features checks, the plain-day cells (`(0.25, 0.25, 23.75, 23.75, 23.0)` and `1.75`) hold under every mutant above. Only the transition-day cells move.

## Figures

The finding harness `dev/audit/harnesses/r11_wallclock_dst.py` (new in this PR; this pass adds `next_window_census`; sha1 `ecae8ba9c8331a1bfd6a2d00f141be21db5cdc95` at this head). It exits 1 when the instance disagrees with the zone's clock on that day, 0 when it agrees, and 2 on a probe precondition, so a skipped arm never reads as agreement. Command, run at each end with that end's `custom_components` and this head's harness file:
`PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r11_wallclock_dst.py <instance> --day <day>`

| instance | base 46d0a521be spring / autumn / plain | this head spring / autumn / plain |
|---|---|---|
| hours_until_next_window | 3.5 vs 2.5 / 3.5 vs 4.5 / 3.5 agrees | agrees / agrees / agrees |
| simulate_trajectory | 88 of 96 steps off / 84 / 0 | 0 / 0 / 0 |
| simulate_trajectory_batch | 88 / 84 / 0 | 0 / 0 / 0 |
| simulate_trajectory_with_dhw | 176 of 192 reads off / 168 / 0 | 0 / 0 / 0 |

`next_window_census` is the rule enumerating the countdown's domain. It takes each 2026 day on which the zone's UTC offset grows (`spring`) or shrinks (`autumn`), plus 10 June (`plain`), in Europe/Stockholm, Australia/Sydney (southern), Australia/Lord_Howe (a 30-minute shift) and America/Santiago (a shift at local midnight). On each, it drives every quarter-hour wall `now` of the day (both passes of a repeated hour) against a one-window schedule at every quarter-hour start, 5 and 90 minutes long, the first shorter and the second longer than any jump. The oracle is the zone's own clock, walked minute by minute in UTC: the window opens at the first minute after `now` whose local (date, wall time) lies inside today's or tomorrow's window and whose previous minute's does not.

| ref | spring | autumn | plain |
|---|---|---|---|
| base `46d0a521be` | 4293 of 71040 cells off | 14300 of 76416 | 0 of 73728 |
| reviewed head `411932cae1` | 136 of 71040 | 76 of 76416 | 0 of 73728 |
| this head | 0 of 71040 | 0 of 76416 | 0 of 73728 |

Class seams, step 8. The claim quantifies over two sets of production sites, each the output of a named rule over `custom_components/*.py`, and over the countdown's input domain, which `next_window_census` enumerates above:

- Rule A, an hour of day advanced by an elapsed step: `git grep -nE "%[[:space:]]*24(\.0)?\b" <ref> -- 'custom_components/*.py' | grep -E "\*[[:space:]]*(dt|step|self\.dt|h\.dt)|dt_hours|\+="` together with `git grep -nE "hour[a-z_]*[[:space:]]*\+=[[:space:]]*(dt|step)" <ref> -- 'custom_components/*.py'`. At the base it returns thermal_model.py:4433, 4654, 4903 and 4990, all closed in this diff. At this head it returns nothing. Residue by category: a trajectory given no clock (`step_hours=None`) walks a zoneless day from midnight, so it has no zone and no transition.
- Rule B, a wall-hour difference returned as a duration: `git grep -nE "[+-][[:space:]]*24(\.0)?[[:space:]]*-[[:space:]]*[a-z_.]+|-[[:space:]]*[a-z_]*hour[a-z_]*\)?[[:space:]]*\)?[[:space:]]*%[[:space:]]*24" <ref> -- 'custom_components/*.py'`. At the base it returns dhw_schedule.py:567 (`hours_until_next_window`, closed in this diff) and dhw_schedule.py:600 (`window_minutes`). At this head it returns only the `window_minutes` line, because the countdown no longer computes a wall-hour gap. `window_minutes` is a configured window's nominal length, whose one caller is the config-time length validation (`dhw_schedule.py`, `MIN_WINDOW_MINUTES`). No instant is involved, so this is residue by category.

Architecture score: `python3 tools/audit/archscore/score.py --diff 411932c HEAD` printed `Architecture score: dS +0.0000 NULL` (the repair's delta).

Scoped gate: `python3 tests/closure.py select --diff 46d0a521befa01ff62cf647e04d3a2b783ea2fc1` printed `MODE: SCOPED -- 29 script(s) run, 5 scoped out.` This pass ran, at this head: `tests/structure.py` (`STRUCTURE RATCHET PASSED`), `tests/doc_claims.py` (`ALL 443 checks PASSED`, after a split of one 41-word test comment it first refused) and `tests/dst_checks.py` (137 passed), plus the features block above (`ALL 3 FEATURES BLOCK PASSED`). Per the repair brief, `prepr.sh` ran scoped (`PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`), and the rest of the scope is left to CI. Not run here: mypy (no typing venv on this seat), which the `tests / typing` job runs.

## Unpinned sites

Each site is one this pass adds in `dhw_schedule.py`, under `custom_components/`, which `mutation-autofix` pins once a mutant is killed. A killer named "(run)" was measured with the drive in `## Mutation proof`; the rest are named by reading.
- `custom_components/heatpump_optimizer/dhw_schedule.py:571 BOOLOP` and `custom_components/heatpump_optimizer/dhw_schedule.py:571 GUARD_OFF` (`if windows and hour_in_windows(now.hour + now.minute / 60.0, windows):`): pinned by mutation-autofix; expected killers `inside a demand window the next window is now, not the following one` and `outside one it counts the hours to the next opening, wrapping past midnight`.
- `custom_components/heatpump_optimizer/dhw_schedule.py:579 CMP_BOUND` (`if t > utc_instant(now)`): triaged equivalent in `tests/mutation_ledger/survivor_triage/dhw_schedule.py/hours_until_next_window.CMP_BOUND.e2e8012d.json` (run: the block passed and the census read 0 under `>=`). Equality reaches the filter only for a zero-length window, which `_parse_one_range` refuses.
- `custom_components/heatpump_optimizer/dhw_schedule.py:581 RETURN_DEL` (`return utc_elapsed_seconds(min(opens), now) / 3600.0 if opens else None`): pinned by mutation-autofix; expected killer the countdown check (every cell reads None).
- `custom_components/heatpump_optimizer/dhw_schedule.py:597 GUARD_OFF` (the round-trip guard): pinned by mutation-autofix; killed (run, M3), the countdown check, census spring 156.
- `custom_components/heatpump_optimizer/dhw_schedule.py:604 RETURN_DEL` (`return out`): pinned by mutation-autofix; expected killer the countdown check (iterating None raises).
- `custom_components/heatpump_optimizer/dhw_schedule.py:609 BOOLOP` and `custom_components/heatpump_optimizer/dhw_schedule.py:609 RETURN_DEL` (`_wall_inside`): pinned by mutation-autofix; expected killers the countdown check's jump cells (0.5 h into 01:30-02:15, 1.5 h into 02:30-04:00) and its 24.75 h skipped-window cell.
- `custom_components/heatpump_optimizer/dhw_schedule.py:616 GUARD_OFF` (`if hi.astimezone(zone).utcoffset() == first:`): triaged equivalent in `tests/mutation_ledger/survivor_triage/dhw_schedule.py/_offset_change.GUARD_OFF.171717b6.json` (run: the block passed and the census read 0). Without it a plain day's bisection returns the next midnight, whose wall date `_wall_inside` refuses; the guard saves work only.
- `custom_components/heatpump_optimizer/dhw_schedule.py:618 CMP_BOUND` (`while hi - lo > timedelta(seconds=1):`): pinned by mutation-autofix; killed (run) by non-termination: under `>=`, `mid` equals `lo` at a one-second gap, and the block timed out (rc 124 under `timeout 60`).
- `custom_components/heatpump_optimizer/dhw_schedule.py:621 RETURN_DEL` (`return hi`): pinned by mutation-autofix; expected killer the countdown check's spring cell (1.5 h to the jump into 02:30-04:00; with no jump the start does not exist and the next opening is tomorrow).

The five ledger entries this PR's earlier rounds and main held for `hours_until_next_window` named lines the repair removed (`ci_predict.py`: `STALE PIN ... disposition names no site the inventory generates`). They are deleted: killed_by `BOOLOP 9ca8508f`, `GUARD_OFF 2982fad3`, `GUARD_OFF 9ca8508f` and `RETURN_DEL 056b2341`, and survivor_triage `CMP_BOUND efe0497c`, whose equivalence argument the `e2e8012d` triage carries forward.

## Red checks`.

## Mutation proof

Each mutant was applied alone to `dhw_schedule.py` at this head and restored (`cmp` against the saved fix read identical). Each run uses `tools/audit/seat/features_block.py` from `# P7, issue 3786: a wall-clock hour` to `def _p7_slips(name, day):`, with the block's emitted prelude, plus `next_window_census --day spring|autumn`:

- M0, `dhw_schedule.py` back to the reviewed head `411932c` (the repair removed): FAIL `the next-window countdown runs to the first instant the wall clock enters a window: ...` and FAIL `the circulation pump pre-heats 15 min before a 02:45 window from 02:30 in either pass ...`; census spring 136, autumn 76 of the cells off.
- M1, the start's fold loop `(0, 1)` to `(0,)`: the same two checks FAIL; census spring 0, autumn 47.
- M2, `out.append(jump)` deleted: the countdown check FAILS; census spring 80, autumn 19.
- M3, the round-trip guard `if instant.astimezone(zone).replace(tzinfo=None) == wall.replace(tzinfo=None):` to `if True:`: the countdown check FAILS; census spring 156, autumn 0.

Earlier rounds' proofs for the trajectory seams stand on unchanged lines (`thermal_model.py`, this diff's earlier commits). The restoration of `thermal_model.py` scalar `float(gains_clock[i]) % 24.0` to `(step_hours[0] + i * dt_hours) % 24.0` fails `every trajectory step reads its gains and draw hour off the step clock on both DST days and a plain one (scalar, batched, with hot water)`. This pass re-ran none of those per mutant.

`tests/dst_checks.py`, the wall-clock tracer (round-9 P7 barrier), under `HASTUB_TZ=Europe/Stockholm` at this head: `ALL 137 DST / QUARTER-GRID CHECKS PASSED`. The new route walks no zoned stamp with `+ timedelta`. Every step is a `datetime.combine` or a UTC instant.

## Null control

The plain day (2026-06-10) is each arm's null control. `next_window_census --day plain` reads 0 cells off at the merge base, at the reviewed head and at this head. Had the census oracle disagreed with the function on ordinary days, it would have read off there. In the new features checks, the plain-day cells (`(0.25, 0.25, 23.75, 23.75, 23.0)` and `1.75`) hold under every mutant above. Only the transition-day cells move.

## Figures

The finding harness `dev/audit/harnesses/r11_wallclock_dst.py` (new in this PR; this pass adds `next_window_census`; sha1 `ecae8ba9c8331a1bfd6a2d00f141be21db5cdc95` at this head). It exits 1 when the instance disagrees with the zone's clock on that day, 0 when it agrees, and 2 on a probe precondition, so a skipped arm never reads as agreement. Command, run at each end with that end's `custom_components` and this head's harness file:
`PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r11_wallclock_dst.py <instance> --day <day>`

| instance | base 46d0a521be spring / autumn / plain | this head spring / autumn / plain |
|---|---|---|
| hours_until_next_window | 3.5 vs 2.5 / 3.5 vs 4.5 / 3.5 agrees | agrees / agrees / agrees |
| simulate_trajectory | 88 of 96 steps off / 84 / 0 | 0 / 0 / 0 |
| simulate_trajectory_batch | 88 / 84 / 0 | 0 / 0 / 0 |
| simulate_trajectory_with_dhw | 176 of 192 reads off / 168 / 0 | 0 / 0 / 0 |

`next_window_census` is the rule enumerating the countdown's domain. It takes each 2026 day on which the zone's UTC offset grows (`spring`) or shrinks (`autumn`), plus 10 June (`plain`), in Europe/Stockholm, Australia/Sydney (southern), Australia/Lord_Howe (a 30-minute shift) and America/Santiago (a shift at local midnight). On each, it drives every quarter-hour wall `now` of the day (both passes of a repeated hour) against a one-window schedule at every quarter-hour start, 5 and 90 minutes long, the first shorter and the second longer than any jump. The oracle is the zone's own clock, walked minute by minute in UTC: the window opens at the first minute after `now` whose local (date, wall time) lies inside today's or tomorrow's window and whose previous minute's does not.

| ref | spring | autumn | plain |
|---|---|---|---|
| base `46d0a521be` | 4293 of 71040 cells off | 14300 of 76416 | 0 of 73728 |
| reviewed head `411932cae1` | 136 of 71040 | 76 of 76416 | 0 of 73728 |
| this head | 0 of 71040 | 0 of 76416 | 0 of 73728 |

Class seams, step 8. The claim quantifies over two sets of production sites, each the output of a named rule over `custom_components/*.py`, and over the countdown's input domain, which `next_window_census` enumerates above:

- Rule A, an hour of day advanced by an elapsed step: `git grep -nE "%[[:space:]]*24(\.0)?\b" <ref> -- 'custom_components/*.py' | grep -E "\*[[:space:]]*(dt|step|self\.dt|h\.dt)|dt_hours|\+="` together with `git grep -nE "hour[a-z_]*[[:space:]]*\+=[[:space:]]*(dt|step)" <ref> -- 'custom_components/*.py'`. At the base it returns thermal_model.py:4433, 4654, 4903 and 4990, all closed in this diff. At this head it returns nothing. Residue by category: a trajectory given no clock (`step_hours=None`) walks a zoneless day from midnight, so it has no zone and no transition.
- Rule B, a wall-hour difference returned as a duration: `git grep -nE "[+-][[:space:]]*24(\.0)?[[:space:]]*-[[:space:]]*[a-z_.]+|-[[:space:]]*[a-z_]*hour[a-z_]*\)?[[:space:]]*\)?[[:space:]]*%[[:space:]]*24" <ref> -- 'custom_components/*.py'`. At the base it returns dhw_schedule.py:567 (`hours_until_next_window`, closed in this diff) and dhw_schedule.py:600 (`window_minutes`). At this head it returns only the `window_minutes` line, because the countdown no longer computes a wall-hour gap. `window_minutes` is a configured window's nominal length, whose one caller is the config-time length validation (`dhw_schedule.py`, `MIN_WINDOW_MINUTES`). No instant is involved, so this is residue by category.

Architecture score: `python3 tools/audit/archscore/score.py --diff 411932c HEAD` printed `Architecture score: dS +0.0000 NULL` (the repair's delta).

Scoped gate: `python3 tests/closure.py select --diff 46d0a521befa01ff62cf647e04d3a2b783ea2fc1` printed `MODE: SCOPED -- 29 script(s) run, 5 scoped out.` This pass ran, at this head: `tests/structure.py` (`STRUCTURE RATCHET PASSED`), `tests/doc_claims.py` (`ALL 443 checks PASSED`, after a split of one 41-word test comment it first refused) and `tests/dst_checks.py` (137 passed), plus the features block above (`ALL 3 FEATURES BLOCK PASSED`). Per the repair brief, `prepr.sh` ran scoped (`PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`), and the rest of the scope is left to CI. Not run here: mypy (no typing venv on this seat), which the `tests / typing` job runs.

## Unpinned sites

Each added `custom_components/` site of this pass is in `dhw_schedule.py`, which `mutation-autofix` pins. The killers named are by the run under `## Mutation proof` where it ran, else by reading:
- `_window_entries`'s fold loop, `out.append(instant)` and the round-trip guard: killed (M1, M3), the countdown check.
- `_window_entries`'s jump branch (`if jump is not None and _wall_inside(...) and not _wall_inside(...)`, `out.append(jump)`): killed (M2), the countdown check (0.5 h to the jump back into 01:30-02:15; 1.5 h to the jump into 02:30-04:00).
- `_offset_change`'s early `return None` and its bisection: expected killer the countdown check's spring cells (1.5 h needs the jump to the second), and on the plain day a bogus jump inside a window would move the plain cells.
- `_wall_inside`: expected killer the countdown check's 24.75 h skipped-window cell (it returns False after the jump).
- `hours_until_next_window`'s `if t > utc_instant(now)` filter and the `else None`: expected killers the countdown check (23.75 h from the second pass) and `with no windows configured there is no answer, which is not 'now'`.

## Red checks

- `tests / mutation`: predicted red on the added `custom_components/` sites listed under `## Unpinned sites`. `mutation-autofix` pins them (`ci: pin killed mutants`, ci-autofix.md); the pin is `unmeasured` until it runs on this head. The cheaper detector already ran: the per-line mutants in `## Mutation proof`, run locally before the push, at a standing cost of one features block and two census runs per mutant (seconds). No further detector is owed.
- `budget-raise-gate / budget-raise-gate`: red at the reviewed head's earlier rounds, whose diff raised `name_kept_members`. Over `46d0a521be...` this head, no budget leaf in any `*_budgets.json` is raised (the three-dot diff of `tests/structure_budgets.json` only lowers `class_excess_loc` and `module_excess_loc`), so the gate has nothing to hold and reads green on its next run at this head. Cheaper detector: `tests/structure.py`, which refuses a breach locally before any push, at a standing cost of one ratchet run per push. No further detector is owed.
- `tests / coverage-ratchet`: `prepr.sh`'s body check read it red at this seat's run. This seat found no failed run of it. At the reviewed head `411932cae1`, PR #3914's check runs list no `coverage-ratchet` job, and `tests / coverage`, which it waits on, was `in_progress` at 2026-11-27T01:00Z. The cause is therefore unmeasured here and is not answered as this diff's. The lines this pass adds are all in `dhw_schedule.py`, and the P7 features block drives each of them (its mutants above are killed by that block or the census), so the pass adds no line the gate leaves unexecuted. Cheaper detector: none locally. `tests/coverage_ratchet.py` needs the coverage payload of a full gate run, and `prepr.sh` lists it as pinned elsewhere for that reason; the lane itself is the detector, at its standing CI cost.
- `governance / wave-script`: if `ci_predict.py` reads `AGREEMENT UNMERGED`, that comes from the predictor's plain merge. `git merge-tree --write-tree origin/main HEAD` exits 0, resolving `tests/closures.json` through the `ledgermerge` driver, which the predictor does not apply. The cheaper detector is that merge-tree run.

## Forward-carry

- The trajectory entry points (`simulate_trajectory`, `simulate_trajectory_batch`, `simulate_trajectory_with_dhw`) take `step_hours`, the step clock, and no longer take `start_hour`. `hours_until_next_window` and `vvc_should_run` take an aware `now`, not a float hour. A branch cut before this merge that calls the old keyword or passes a float raises `TypeError` or `AttributeError`. The control is `dev/audit/harnesses/r11_wallclock_dst.py`, exit 1 on either transition day. The constraint detects itself: a stale call raises on its first use, under that group's own gate run. Carry: dismissed: a stale caller fails loudly under its own scoped gate, and the learners group cannot be named (see Friction)
- The same constraint for the DHW schedule callers: `hours_until_next_window(now, ...)` measures between instants, and a planner horizon must carry `start_time`. Carry: R11-OUTSIDE-HONEST-DHW-RUNS

## Friction

- brief-citations: stale: the group's brief names "the one naive-instant zone definition R11-SEAM-kernel-step puts in const"; #3728 landed it as `drift.utc_instant`, and `const.py` holds no zone definition. Carry: dismissed: the brief is consumed by this pull request
- carry-audit: contradiction: `tools/audit/carry_audit.py`'s `GROUP_TOK` (`\A[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\Z`) refuses every roster group id with a lower-case tail, so `Carry: R11-SEAM-learners`, the live group this brief lists as a valid target, reads UNROUTED, and the upper-cased spelling reads BAD-DEST. Carry: dismissed: tooling owned by the orchestrator, reported in the seat result
- dispatch-payload: contradiction: the payload's Output section names the return refs `handoff/r11-repair-3914` and `handoff-body/r11-repair-3914`, and its brief step 4 names `handoff/r11-seam-wallclock-dst`; this seat pushed the payload's refs, the only ones it may write. Carry: dismissed: dispatch tooling owned by the orchestrator, reported in the seat result
