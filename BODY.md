Closes #3786

R11-SEAM-wallclock-dst (class P7 residual). Four production seams carried a wall-clock hour across a DST change as if every day had 24 h:

- `ThermalModel.simulate_trajectory`, `simulate_trajectory_batch` and `simulate_trajectory_with_dhw` derived each step's hour of day as `start_hour + i * dt_hours`. On a transition day, from the change onward, every step read the learned internal-gains profile (and, for the DHW twin, the draw pattern) an hour off the step clock the optimizer builds (`optimizer._step_clock`, walked in UTC by `drift.utc_step_starts`). They now take that clock as `step_hours` and do no clock arithmetic of their own. Every production caller already held it (`h.step_hours`); `_optimize_with_dhw` no longer recomputes `start_time.hour + start_time.minute / 60`. With no clock, `simulate_trajectory_with_dhw` keeps its former default, a zoneless day from midnight.
- `dhw_schedule.hours_until_next_window` returned the wall-clock gap as a duration, which is 3.5 h from 00:30 to a 04:00 window when the spring-forward day holds 2.5 real hours. It now takes the aware `now` and builds the window's wall instant from its date and minute (`datetime.combine`, so no `+ timedelta` walks a zoned stamp). It measures the gap between the two instants with `drift.utc_elapsed_seconds`, which reads a naive instant through the kernel-step definition `drift.utc_instant`. Its three callers pass an instant: the coordinator's published countdown (`dt_util.now()`), the VVC pre-heat lead (`pump_schedule.vvc_should_run`, now taking `now`), and the planner's `next_window_in_hours`. The planner passes `h.start_time`, which its horizon protocol now declares.

The brief places the naive-instant definition "in const". Kernel-step landed it as `drift.utc_instant` (#3728), and this diff reads it there.

The brief's three instances are fixed, plus `simulate_trajectory_with_dhw`, which the issue's sweep lists (three times) and the brief omits. D15-s2-04 (unreproduced at judging) is recorded and not edited: its harness (`m5_zone.py --bundle B`) needs a diagnostics bundle the tree does not carry, and the register records `debug_replay.py` with 0 occurrences of `HASTUB_TZ`.

## Head

4edae55888adc266403a5d2325d62daa2de79cf8, measured on origin/main dbdc71faea358a95a7b33840ed252b0d8a646a31 (the merge base), 2026-11-26T10:26:54Z.

## Mutation proof

Each pre-fix predicate restored alone, the rest of the head kept. Each run uses `tools/audit/seat/features_block.py` from `# The countdown the optimizer publishes as` to `# dhw_planner`, with the block's emitted prelude plus a `_WS` prelude:

- `thermal_model.py` scalar, `float(gains_clock[i]) % 24.0` back to `(step_hours[0] + i * dt_hours) % 24.0`: FAIL `every trajectory step reads its gains and draw hour off the step clock on both DST days and a plain one (scalar, batched, with hot water)`, with `('scalar','spring'): 88, ('scalar','autumn'): 84, ('scalar','plain'): 0`.
- the batched twin's `hour_i`, the same restoration: the same check FAILS, with `('batch','spring'): 88`.
- `simulate_trajectory_with_dhw`'s `hours`, back to `step_hours[0] + np.arange(n_steps) * dt_hours`: the same check FAILS, on the `dhw` cells.
- `dhw_schedule.py`, `return utc_elapsed_seconds(opens, now) / 3600.0` back to `return min(starts)`: FAIL `the next-window countdown is the zone's real hours across a DST change (00:30 to a 04:00 window: 2.5 h spring, 4.5 h autumn, 3.5 h plain)`, with `{'spring': 3.5, 'autumn': 3.5, 'plain': 3.5}`.

`tests/dst_checks.py`'s wall-clock tracer (round-9 P7 barrier) independently refused this diff's first countdown, which walked `now + timedelta(hours=...)`: `FAIL no production seam does wall-clock arithmetic across either transition [spring [('dhw_schedule.py', 'hours_until_next_window')] ...]`. The `datetime.combine` route reads no seam (`dst_checks.py` rc 0 under `HASTUB_TZ=Europe/Stockholm`).

## Null control

The plain day (2026-06-10, Europe/Stockholm) is each arm's null control. At the merge base every probe reads 0 slips and a 3.5 h countdown there, and fails only on the transition days. In the new checks, the plain cell reads 0 under every mutant.

## Figures

The finding harness `dev/audit/harnesses/r11_wallclock_dst.py` (new; the issue's `probe_p7.py` exists at no ref). It exits 1 when the instance disagrees with the zone's clock on that day, 0 when it agrees, and 2 on a probe precondition, so a skipped arm never reads as agreement. Command, run at both ends for each instance and each `--day spring|autumn|plain`:
`PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r11_wallclock_dst.py <instance> --day <day>`

| instance | base dbdc71faea spring / autumn / plain | head spring / autumn / plain |
|---|---|---|
| hours_until_next_window | rc 1 (3.5 vs 2.5) / rc 1 (3.5 vs 4.5) / rc 0 | rc 0 / rc 0 / rc 0 |
| simulate_trajectory | rc 1 (88 of 96 steps) / rc 1 (84) / rc 0 | rc 0 / rc 0 / rc 0 |
| simulate_trajectory_batch | rc 1 (88) / rc 1 (84) / rc 0 | rc 0 / rc 0 / rc 0 |
| simulate_trajectory_with_dhw | rc 1 (176 of 192 reads) / rc 1 (168) / rc 0 | rc 0 / rc 0 / rc 0 |

Class seams, step 8. The claim quantifies over two sets, each the output of a named rule over `custom_components/*.py`:

- Rule A, an hour of day advanced by an elapsed step: `git grep -nE "%[[:space:]]*24(\.0)?\b" <ref> -- 'custom_components/*.py' | grep -E "\*[[:space:]]*(dt|step|self\.dt|h\.dt)|dt_hours|\+="` together with `git grep -nE "hour[a-z_]*[[:space:]]*\+=[[:space:]]*(dt|step)" <ref> -- 'custom_components/*.py'`. At the base it returns thermal_model.py:4433, 4654, 4903 and 4990, all closed in this diff. At the head it returns nothing. Residue by category: a trajectory given no clock (`step_hours=None`) walks a zoneless day from midnight, so it has no zone and no transition.
- Rule B, a wall-hour difference returned as a duration: `git grep -nE "[+-][[:space:]]*24(\.0)?[[:space:]]*-[[:space:]]*[a-z_.]+|-[[:space:]]*[a-z_]*hour[a-z_]*\)?[[:space:]]*\)?[[:space:]]*%[[:space:]]*24" <ref> -- 'custom_components/*.py'`. At the base it returns dhw_schedule.py:567 (`hours_until_next_window`, closed in this diff) and dhw_schedule.py:600 (`window_minutes`). At the head it returns the same two lines: :574, now the wall-hour gap the instants measure, and :610, `window_minutes`. `window_minutes` is a configured window's nominal length, whose one caller is the config-time length validation (`dhw_schedule.py`, `MIN_WINDOW_MINUTES`). No instant is involved, so this is residue by category.

Architecture score: `python3 tools/audit/archscore/score.py --diff dbdc71faea358a95a7b33840ed252b0d8a646a31 HEAD` printed `Architecture score: dS +0.0000 NULL`.

Scoped gate: `python3 tests/closure.py select --diff dbdc71faea358a95a7b33840ed252b0d8a646a31` printed `MODE: SCOPED` and named 28 scripts. The scoped `tests/run.sh` (`GATE_SCOPE=auto GOLDEN_MODE=drift`) ran at an earlier head of this branch. `features.py` (through `dst_checks.py`), `doc_claims.py`, `typing_ruler.py` and `structure.py` went red there, and the later commits fix each: the tracer route, the 40-word docstring sentence, mypy's two `index` errors and one `attr-defined` error, and the recorded raise. Each was then re-run alone at this head: `dst_checks.py` rc 0, `doc_claims.py` 0 FAIL, mypy `Success: no issues found`, `structure.py` no FAIL, and `features.py` 1 of 6224 FAIL. That one is `_bootstrap drops the package directory so datetime is stdlib`, which fails only because the direct run puts `custom_components` on `PYTHONPATH`; it reads `ok` inside `run.sh`. `stress.py` read one memory-peak FAIL in the shared run (0.4 MiB against 0.2 MiB) and `ALL 122 STRESS CHECKS PASSED` alone under the lease.

## Raise justification

`name_kept_members` 38 -> 39. The DHW planner's horizon protocol (`dhw_planner._Horizon`) declares `start_time`, the instant the next-window countdown is measured from. `tests/structure.py` reads every `Protocol` receiver as untyped by design (its self-test pins that), so any new protocol member counts, whatever its name. Recorded with `--record --allow-regression`, the reason in the commit message, under mandate 6893738184 (scope all, in force to 2026-12-15).

Payments tried: renaming the protocol (no move: the rule keys on the Protocol base, not the name); an explicit `start` parameter on `_build_dhw_requirements` (no move, but a second channel for a field the horizon already carries, refused under fixer.md step 17); deleting an unread protocol member (none exists: `wind_speeds`, `precipitation`, `solar_radiation` and `external_heat_kw` are read through `WeatherSeries.from_horizon`, and `_PlannerConfig.pv_export_price` in the planner's surplus pricing); computing the countdown from the step grid alone (inexact past the horizon end, where tomorrow's window often lies).
Architecture score: dS +0.0000 NULL

## Unpinned sites

Each site below is in `custom_components/`, so `mutation-autofix` pins it. The check named is the one expected to kill it, by reading; none was run per mutant here (step 5 leaves `stress.py` to CI):
- `custom_components/heatpump_optimizer/dhw_planner.py:107 RETURN_DEL` (`return hours_until_next_window(start, today, tomorrow)`): pinned by mutation-autofix; expected killer `the next DHW window on an empty horizon is None, and a repeated hour reads tomorrow as the ordinary day ...` (expects 19.5 and 10.5).
- `custom_components/heatpump_optimizer/dhw_schedule.py:570 BOOLOP` and `custom_components/heatpump_optimizer/dhw_schedule.py:570 GUARD_OFF` (`if windows and hour_in_windows(h, windows):`): pinned by mutation-autofix; expected killers `inside a demand window the next window is now, not the following one` and `outside one it counts the hours to the next opening, wrapping past midnight`.
- `custom_components/heatpump_optimizer/dhw_schedule.py:575 GUARD_OFF` (`if not starts:`): pinned by mutation-autofix; expected killer `with no windows configured there is no answer, which is not 'now'` (`min()` of an empty list raises).
- `custom_components/heatpump_optimizer/dhw_schedule.py:583 RETURN_DEL` (`return utc_elapsed_seconds(opens, now) / 3600.0`): pinned by mutation-autofix; the restoration of this line to `return min(starts)` is killed by the DST countdown check (Mutation proof).
- `custom_components/heatpump_optimizer/pump_schedule.py:68 GUARD_OFF` (`if hour_in_windows(now.hour + now.minute / 60.0, windows):`): pinned by mutation-autofix; expected killer `the VVC pump runs inside a demand window and rests outside`.

## Red checks

- `mutation`: predicted red on the six added `custom_components/` sites listed under `## Unpinned sites`. `mutation-autofix` pins them (`ci: pin killed mutants`, ci-autofix.md); this pin is `unmeasured` until it runs on this head. The cheaper detector already ran: `tools/pr/ci_predict.py` named each site locally before the push, at a standing cost of one predictor run per handoff. No further detector is owed.
- `budget-raise-gate`: predicted red, because this diff raises `name_kept_members` 38 -> 39 in `tests/structure_budgets.json` (see `## Raise justification`). The gate is the approval mechanism itself, and it clears on an approving review that cites mandate 6893738184. No cheaper detector exists: `tests/structure.py` already refused the breach locally, before any push.

## Forward-carry

- The trajectory entry points (`simulate_trajectory`, `simulate_trajectory_batch`, `simulate_trajectory_with_dhw`) take `step_hours`, the step clock, and no longer take `start_hour`. `hours_until_next_window` and `vvc_should_run` take an aware `now`, not a float hour. A branch cut before this merge that calls the old keyword or passes a float raises `TypeError` or `AttributeError`. The control is `dev/audit/harnesses/r11_wallclock_dst.py`, exit 1 on either transition day. The constraint detects itself: a stale call raises on its first use, under that group's own gate run. Carry: dismissed: a stale caller fails loudly under its own scoped gate, and the learners group cannot be named (see Friction)
- The same constraint for the DHW schedule callers: `hours_until_next_window(now, ...)` measures between instants, and a planner horizon must carry `start_time`. Carry: dismissed: the destination brief does not yet hold this line and no roster branch is open to this seat; the orchestrator lands it (opener report)

## Friction

- brief-citations: stale: the group's brief names "the one naive-instant zone definition R11-SEAM-kernel-step puts in const"; #3728 landed it as `drift.utc_instant`, and `const.py` holds no zone definition. Carry: dismissed: the brief is consumed by this pull request
- carry-audit: contradiction: `tools/audit/carry_audit.py`'s `GROUP_TOK` (`\A[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\Z`) refuses every roster group id with a lower-case tail, so `Carry: R11-SEAM-learners`, the live group this brief lists as a valid target, reads UNROUTED, and the upper-cased spelling reads BAD-DEST. Carry: dismissed: tooling owned by the orchestrator, reported in the seat result
