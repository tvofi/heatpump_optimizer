Closes #3786

R11-SEAM-wallclock-dst (class P7 residual). Four production seams carried a wall-clock hour across a DST change as if every day had 24 h:

- `ThermalModel.simulate_trajectory`, `simulate_trajectory_batch` and `simulate_trajectory_with_dhw` derived each step's hour of day as `start_hour + i * dt_hours`. On a transition day, from the change onward, every step read the learned internal-gains profile (and, for the DHW twin, the draw pattern) an hour off the step clock the optimizer builds (`optimizer._step_clock`, walked in UTC by `drift.utc_step_starts`). They now take that clock as `step_hours` and do no clock arithmetic of their own. Every production caller already held it (`h.step_hours`); `_optimize_with_dhw` no longer recomputes `start_time.hour + start_time.minute / 60`. With no clock, `simulate_trajectory_with_dhw` keeps its former default, a zoneless day from midnight.
- `dhw_schedule.hours_until_next_window` returned the wall-clock gap as a duration, which is 3.5 h from 00:30 to a 04:00 window when the spring-forward day holds 2.5 real hours. It now takes the aware `now` and builds the window's wall instant from its date and minute (`datetime.combine`, so no `+ timedelta` walks a zoned stamp). It measures the gap between the two instants with `drift.utc_elapsed_seconds`, which reads a naive instant through the kernel-step definition `drift.utc_instant`. Its three callers pass an instant: the coordinator's published countdown (`dt_util.now()`), the VVC pre-heat lead (`pump_schedule.vvc_should_run`, now taking `now`), and the planner's `next_window_in_hours`. The planner passes `h.start_time`, which its horizon protocol now declares.

The brief places the naive-instant definition "in const". Kernel-step landed it as `drift.utc_instant` (#3728), and this diff reads it there.

The brief's three instances are fixed, plus `simulate_trajectory_with_dhw`, which the issue's sweep lists (three times) and the brief omits. D15-s2-04 (unreproduced at judging) is recorded and not edited: its harness (`m5_zone.py --bundle B`) needs a diagnostics bundle the tree does not carry, and the register records `debug_replay.py` with 0 occurrences of `HASTUB_TZ`.

## Head

`57b249813e9f71bfeee329fc00106d109e8e7c46` merges the authored code head `efda938a30a6dcafa32fd23bbc41bf2966b3e73a`.

Repair commit on top of `352a829c6ae31e1022d4f47d08022a004d9013a3`: the survivor_triage entry for `dhw_schedule.py:618` (see `## Red checks

Red at head `57b24981` (`gh pr checks 3914`, run 46028388737), then the earlier heads' reds by check name.

- `tests / mutation` at `57b24981`: `MUTATION TABLE REFUSED` on one stale disposition, flow_lift.py `FlowCurveBias.observe_temps` BOOLOP 04143c3f (old pin `if return_temp is not None and np.isfinite(return_temp)`). This diff does not touch flow_lift.py: inherited from main, cured by #3939. No repair here.
- `tests / mutation-autofix` at `57b24981`: owed only for sites this diff added unpinned; `mutation-pins` was queued behind the runner backlog, so unmeasured. It cannot clear the inherited stale pin above; inherited from main, cured by #3939.
- `tests / fast (3.14, 2/4)` at `57b24981`: `python3 tests/features.py` ended on `TypeError: ThermalModel.simulate_trajectory_batch() got an unexpected keyword argument 'start_hour'` at tests/features.py:7100. Cause: `_r11pp_batch`, landed on main by the plant-pins PR, still passes `start_hour=7.0` to the entry points whose keyword this diff removes (`## Forward-carry`). Fixed by 8bf9676b8a0f (`step_hours=(7.0 + arange(n)*0.25) % 24` to both calls), not run to completion locally. Cheaper detector: `python3 tests/features.py`, whose single-shard cost is the standing cost.
- `tests / fast (3.14, 3/4)`: the shard-3 `tests/open_meteo.py` failure of an earlier head, answered below under `tests / fast (3.14)`; cured at a later head.
- `gate`: red because it aggregates `tests / mutation` and `tests / fast (3.14, 2/4)`; no check of its own.
- `tests / nightly-status`: reports the scheduled nightly on main, not this diff; clears on the next green nightly.

Earlier heads:

`352a829c6ae31e1022d4f47d08022a004d9013a3` merges the authored code head `b39d46e1cc4d7c30e60343f0da74d4f766b3819e` and then merges origin/main `e84856520d` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

Merge note: origin/main merged into the branch; tests/structure_budgets.json auto-resolved to the branch values (class_excess_loc 17207, module_excess_loc 21620), both lower than main; no metric raised.
`afe5af2cd3c0c74e72a352127ef79b37ed0be18e` merges the authored code head `b39d46e1cc4d7c30e60343f0da74d4f766b3819e` and then merges origin/main `e84856520d` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`4863ec0529f6eb7802288add93a5612557d5c2b8` merges the authored code head `e77c068d2794656da2cdf39a0786194c332f262d`.

`07cfe69cb4178d929038e8e9b099d86ba48b66bc` merges the authored code head `e77c068d2794656da2cdf39a0786194c332f262d`.

`e77c068d2794656da2cdf39a0786194c332f262d`, merge base `46d0a521befa01ff62cf647e04d3a2b783ea2fc1`, origin/main at `190ffb10c230b6beaf77593b2926d55682e37f47`, 2026-11-27T02:28:54Z. `git merge-tree --write-tree origin/main HEAD` exits 0.

It merges `411932cae1`, the pull request branch tip, into the repair commit `c5bb97a7db72ef1354b2e26c20a45bebf43cfa21`. The repair commit sits on `3cc17d3993eafc175d8e8569f6f5c82ba9102296`, which merges the authored code head `b05510fc75837c7e26877bf2f6dc349e0128b77a`. `411932cae1` carries `d4b31e688a`, a second repair of the same red that deleted the `observed` check. The merge resolves `tests/open_meteo.py` to the repair commit's copy, which keeps that check on `diagnostics()`, and adapts `d4b31e688a`'s one later comment. The production code is unchanged from `b05510fc75`. `git diff c5bb97a7db HEAD` is that single comment line in `tests/open_meteo.py`, so the figures below measured at `c5bb97a7db` describe this tree. `python3 tests/open_meteo.py` re-read `ALL OPEN-METEO CHECKS PASSED` at `e77c068d27`.

## Mutation proof

Each pre-fix predicate restored alone, the rest of the head kept. Each run uses `tools/audit/seat/features_block.py` from `# The countdown the optimizer publishes as` to `# dhw_planner`, with the block's emitted prelude plus a `_WS` prelude:

- `thermal_model.py` scalar, `float(gains_clock[i]) % 24.0` back to `(step_hours[0] + i * dt_hours) % 24.0`: FAIL `every trajectory step reads its gains and draw hour off the step clock on both DST days and a plain one (scalar, batched, with hot water)`, with `('scalar','spring'): 88, ('scalar','autumn'): 84, ('scalar','plain'): 0`.
- the batched twin's `hour_i`, the same restoration: the same check FAILS, with `('batch','spring'): 88`.
- `simulate_trajectory_with_dhw`'s `hours`, back to `step_hours[0] + np.arange(n_steps) * dt_hours`: the same check FAILS, on the `dhw` cells.
- `dhw_schedule.py`, `return utc_elapsed_seconds(opens, now) / 3600.0` back to `return min(starts)`: FAIL `the next-window countdown is the zone's real hours across a DST change (00:30 to a 04:00 window: 2.5 h spring, 4.5 h autumn, 3.5 h plain)`, with `{'spring': 3.5, 'autumn': 3.5, 'plain': 3.5}`.

`tests/dst_checks.py`'s wall-clock tracer (round-9 P7 barrier) independently refused this diff's first countdown, which walked `now + timedelta(hours=...)`: `FAIL no production seam does wall-clock arithmetic across either transition [spring [('dhw_schedule.py', 'hours_until_next_window')] ...]`. The `datetime.combine` route reads no seam (`dst_checks.py` rc 0 under `HASTUB_TZ=Europe/Stockholm`).

- The repair (`tests/open_meteo.py`, `c5bb97a7db`): `open_meteo.py` diagnostics `"observed_points": len(self._observed.times)` mutated to `len(self._forecast.times)`: FAIL `diagnostics count the observed series as observed, not the forecast one` (`got observed_points=5 forecast_points=5`), plus the older `diagnostics report both series`. Null control: under the same mutant with the former equal-length planted series (5 observed points), the new check reads `ok`. That is why the planted observed series now has 3 points, and the fixture assert refuses equal lengths.

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

Repair at `c5bb97a7db`, each run with `PYTHONPATH=tests/hastub` from the worktree root:
- `python3 tests/open_meteo.py`: rc 1 at `3cc17d3993` (`AttributeError: 'OpenMeteoSolar' object has no attribute 'observed'`, tests/open_meteo.py:504), rc 0 at origin/main `fd93aa3e9b` (the null control: main keeps the property), rc 0 `ALL OPEN-METEO CHECKS PASSED` at `c5bb97a7db`.
- `python3 tests/doc_claims.py`: rc 0, `ALL 443 checks PASSED`, at `c5bb97a7db`.
- `python3 tests/entities.py`: rc 0, `ALL 2786 ENTITY CHECKS PASSED`, at `c5bb97a7db`.
- `python3 tests/structure.py`: rc 0, `ok   name_kept_members 38 <= 38`, at `c5bb97a7db`. `git diff 46d0a521be...HEAD -- tests/structure_budgets.json` shows no `name_kept_members` line: the diff no longer raises it, because `3e618a5f60` paid the `_Horizon.start_time` member by deleting `OpenMeteoSolar.observed`. The earlier `## Raise justification` (38 -> 39) described a raise that is no longer in the diff, so it is withdrawn.
- Architecture score: `python3 tools/audit/archscore/score.py --diff 46d0a521befa01ff62cf647e04d3a2b783ea2fc1 HEAD` printed `Architecture score: dS +0.0000 NULL`.
- Scoped gate: `python3 tests/closure.py select --diff 46d0a521befa01ff62cf647e04d3a2b783ea2fc1` printed `MODE: SCOPED -- 29 script(s) run, 5 scoped out.`, and its `scope.run` names `tests/open_meteo.py`.
- Diff mutants: prepr at `c5bb97a7db` (same production lines) printed `WARN     diff mutants           25 survivor(s) on the diff's added lines -- each owes a killing check or a line under ## Unpinned sites (fixer.md step 2)`. Each survivor's line is under `## Unpinned sites`.

## Unpinned sites

`MUTANT_CMD` is the group's finding harness over every instance and day: `bash -c 'for i in hours_until_next_window simulate_trajectory simulate_trajectory_batch simulate_trajectory_with_dhw; do for d in spring autumn plain; do PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r11_wallclock_dst.py "$i" --day "$d" >/dev/null 2>&1 || exit 1; done; done'`. It takes about 7 s per run. The `features_block.py "# The countdown the optimizer publishes as"` call refused as MUTANT_CMD, because its baseline fails on the unedited tree (`NameError: name '_parse_w' is not defined`). Its `--emit-prelude` had not finished after more than 30 minutes, so it is too slow to drive 40 mutants. `mutant_run.py --diff 46d0a521be...HEAD --max-mutants 40 --report-only` reported 25 SURVIVED of the first 40 mutants. The harness pins the four instance bodies, not their callers or the guards around them. Each survivor and its disposition:

- `custom_components/heatpump_optimizer/coordinator.py:6045 CONST_SWAP  dt_util.now(), self._dhw_effective_windows(), self._dhw_effective_windows(2)`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/coordinator.py:6044 STMT_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/dhw_planner.py:106 RETURN_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/dhw_planner.py:815 STMT_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/dhw_planner.py:1243 STMT_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/dhw_schedule.py:569 CONST_SWAP  h = now.hour + now.minute / 120.0`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/dhw_schedule.py:570 GUARD_OFF  if False:`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/dhw_schedule.py:575 GUARD_OFF  if False:`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/dhw_schedule.py:576 RETURN_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/dhw_schedule.py:571 BOOLOP  if windows and hour_in_windows(now.hour + now.minute / 60.0, windows):`: pinned by mutation-autofix (its lane mutates `custom_components/`); `unmeasured` until it runs on this head.
- `custom_components/heatpump_optimizer/dhw_schedule.py:571 GUARD_OFF  if False:`: pinned by mutation-autofix (its lane mutates `custom_components/`); `unmeasured` until it runs on this head.
- `custom_components/heatpump_optimizer/dhw_schedule.py:581 RETURN_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`); `unmeasured` until it runs on this head.
- `custom_components/heatpump_optimizer/dhw_schedule.py:597 GUARD_OFF  if False:`: pinned by mutation-autofix (its lane mutates `custom_components/`); `unmeasured` until it runs on this head.
- `custom_components/heatpump_optimizer/dhw_schedule.py:604 RETURN_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`); `unmeasured` until it runs on this head.
- `custom_components/heatpump_optimizer/dhw_schedule.py:609 BOOLOP  return wall.date() == on and hour_in_windows(wall.hour + wall.minute / 60.0, windows)`: pinned by mutation-autofix (its lane mutates `custom_components/`); `unmeasured` until it runs on this head.
- `custom_components/heatpump_optimizer/dhw_schedule.py:609 RETURN_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`); `unmeasured` until it runs on this head.
- `custom_components/heatpump_optimizer/dhw_schedule.py:618 CMP_BOUND  while hi - lo >= timedelta(seconds=1):`: pinned by mutation-autofix (its lane mutates `custom_components/`); `unmeasured` until it runs on this head.
- `custom_components/heatpump_optimizer/dhw_schedule.py:621 RETURN_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`); `unmeasured` until it runs on this head.
- `custom_components/heatpump_optimizer/optimizer.py:2060 CONST_SWAP  valve_targets=h.valve_targets, step_hours=h.step_hours)[5]`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:2057 STMT_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:5216 STMT_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:5437 STMT_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:5522 STMT_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:5810 STMT_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/optimizer.py:5922 STMT_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/pump_schedule.py:42 RETURN_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/pump_schedule.py:68 GUARD_OFF  if False:`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/pump_schedule.py:68 CONST_SWAP  if hour_in_windows(now.hour + now.minute / 120.0, windows):`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/pump_schedule.py:43 STMT_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/pump_schedule.py:75 STMT_DEL  pass`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/thermal_model.py:4432 CONST_SWAP  float(gains_clock[i]) % 48.0 if gains_clock is not None else None`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/thermal_model.py:4648 CONST_SWAP  hour_i = float(gains_clock[i]) % 48.0 if gains_clock is not None else None`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `custom_components/heatpump_optimizer/thermal_model.py:4895 CONST_SWAP  hours = np.asarray(clock, dtype=float) % 48.0`: pinned by mutation-autofix (its lane mutates `custom_components/`).
- `tools/audit/regret_oracle.py:164 CONST_SWAP  step_hours=np.array([t.hour + t.minute / 120.0`: a `tools/` site, which mutation-autofix does not reach. Measured: `python3 -I tools/audit/regret_oracle.py --self-test` reads `SELF-TEST passed (64 arms)` under this mutant and at the baseline, so the self-test does not kill it. It stays unpinned; it needs an in-tree mutant harness for the oracle, which this repair does not build. It is the branch's own line from `5a94300c92`, not this repair's.

## Red checks

- `tests / fast (3.14)` (run 45907627902, job 140208754082, shard 3/4): `python3 tests/open_meteo.py` exited 1 with `AttributeError: 'OpenMeteoSolar' object has no attribute 'observed'` at tests/open_meteo.py:504. Cause: this branch's commit `3e618a5f60` deleted the property as unread. Its caller search covered production loads of `.observed` only, and the check `observed property returns the observed series, not the forecast one` (on main since #573) still read it. A main merge did not cause it: the same script exits 0 at origin/main `fd93aa3e9b`. Process state: `3e618a5f60` was a budget payment committed after the branch's last scoped `tests/run.sh`. Only the budget and archscore checks were re-run for it, not the scope the touched module selects. The scope of `open_meteo.py` names `tests/open_meteo.py`. Repair: the check now pins the same anti-swap property through `diagnostics()`, the production reader of `_observed` that remains, with distinct series lengths (Mutation proof). The check is kept, and so are the getter's removal and the flat budget. Cheaper detector: `tests/closure.py select` plus the scripts its `scope.run` names, re-run after every production commit, including a budget payment. `prepr.sh` step 6 already runs that scope on the committed head, so no new instrument is built. The countermeasure is to run `prepr.sh` after the last production commit rather than before it.
- `tests / mutation` and `tests / mutation-autofix` (run 45977148320): `tests / mutation` read `MUTATION TABLE REFUSED -- 1737 unpinned site(s) against 1738 at the ratchet base, 1 of them added by this diff`: `dhw_schedule.py:618 CMP_BOUND  while hi - lo > timedelta(seconds=1):`. `mutation-autofix` ended `skip-measure-failed`, so no bot commit came. Pinned: `python3 tests/mutation_table.py --pin-killed --base origin/main` at `352a829c6a` was INCONCLUSIVE on Darwin, because the baseline `tests/optimality.py` is red there (`one|summer_negative|shoulder: a recorded claim still has a gap (not stale)`, a solver-float claim off the canonical environment; this diff does not touch it). Re-run with `--scripts tests/features.py`, the one driver that reaches the site, it drove 1 mutant and refused: the `>=` mutant timed out. Cause: `mid = lo + 0 s` once `hi - lo` is one second, so neither bound moves and the loop never ends, and the table counts a timeout as neither killed nor survived. Not equivalent, so recorded as a hand-written `survivor_triage` entry with verdict `gap` (`tests/mutation_ledger/survivor_triage/dhw_schedule.py/_offset_change.CMP_BOUND.eaeb7f67.json`); the unpinned count then reads 1736 against 1738. Survivor: this one site, triaged by hand and not automated. The other 18 sites listed under `## Unpinned sites` were already pinned at the base head. Cheaper detector: `tools/pr/ci_predict.py` already named the site before the push; none further owed.
- `gate`: red because it requires `tests / mutation`, and carries no check of its own failing; it clears when `tests / mutation` is green at the repaired head. Cheaper detector: none, `gate` only aggregates.
- `tests / coverage-ratchet` (run 45907627902, job 140217348060): `FAIL every module >= 95.0 %  (1 below)`, `open_meteo.py: 68.95 %`. This is the same cause as `tests / fast (3.14)`. `tests/open_meteo.py` aborted at :504, so none of its later checks ran, and the module lost the coverage they carry. Measured with `coverage run --include='*/heatpump_optimizer/open_meteo.py' tests/open_meteo.py` (`PYTHONPATH=tests/hastub`, coverage installed to a scratch directory, since the CI venv has none). With `3cc17d3993`'s copy of the script: script rc 1, 70 of 219 statements missed (68 %). With `c5bb97a7db`'s copy: script rc 0, 2 of 219 missed (99 %), above the 95.0 % floor. Cheaper detector: the same `tests/open_meteo.py` run named under `tests / fast (3.14)`, because a script that exits before its end is what drops a module's coverage. No separate instrument is owed.
- `budget-raise-gate / budget-raise-gate`: red on this pull request's earlier heads, which raised `name_kept_members` 38 -> 39. `3e618a5f60` paid that raise by deleting `OpenMeteoSolar.observed`. At `c5bb97a7db`, `git diff 46d0a521be...HEAD -- tests/structure_budgets.json` raises no leaf (prepr: "no budget leaf raised over 46d0a521be...c5bb97a7db"), so the gate has nothing to hold and clears on its run at this head. Cheaper detector: `tests/structure.py` with that three-dot diff, which reads `ok name_kept_members 38 <= 38` here. It already runs before every push, so nothing new is owed.
- `prepr self-test`: `tools/pr/prepr.sh --self-test` reads 569 passed, 2 failed (`an ancestry no commit of which carries any check run skips, never refuses`, `and the skip line names the boundary`). The same two fail on origin/main, reported by the #3908 fixer; this diff does not touch `tools/pr/`. Cheaper detector: none beyond the self-test itself.
- `governance / wave-script`: `ci_predict.py` printed `AGREEMENT UNMERGED: HEAD does not merge into d66452586467`. `git merge-tree --write-tree origin/main HEAD` exits 0, resolving `tests/structure_budgets.json` and `tests/closures.json` through the `ledgermerge` driver, which the predictor's plain merge does not apply; `prepr.sh` read `wave-script 298 passed, 0 failed` at this head. The cheaper detector is that merge-tree run.
- `tests / nightly-status`: its step "Report the last scheduled run's conclusion" reads the last scheduled nightly run, not this diff; it is red while that nightly run is red and clears on the next green nightly. Cheaper detector: none, the check reports a scheduled run this branch cannot move.
- `tests / replay`: the job is cancelled at its 30-minute cap on most runs, returning no verdict; this diff changes no replay input. #3912 (R11 replay timeout) is open and unmerged; it proposes raising that cap to 60 minutes, and this branch does not depend on it. Cheaper detector: none beyond the lane itself, whose cost the owner fixture sets.

## Forward-carry

- The trajectory entry points (`simulate_trajectory`, `simulate_trajectory_batch`, `simulate_trajectory_with_dhw`) take `step_hours`, the step clock, and no longer take `start_hour`. `hours_until_next_window` and `vvc_should_run` take an aware `now`, not a float hour. A branch cut before this merge that calls the old keyword or passes a float raises `TypeError` or `AttributeError`. The control is `dev/audit/harnesses/r11_wallclock_dst.py`, exit 1 on either transition day. The constraint detects itself: a stale call raises on its first use, under that group's own gate run. Carry: dismissed: a stale caller fails loudly under its own scoped gate, and the learners group cannot be named (see Friction)
- The same constraint for the DHW schedule callers: `hours_until_next_window(now, ...)` measures between instants, and a planner horizon must carry `start_time`. Carry: R11-OUTSIDE-HONEST-DHW-RUNS

## Friction

- brief-citations: stale: the group's brief names "the one naive-instant zone definition R11-SEAM-kernel-step puts in const"; #3728 landed it as `drift.utc_instant`, and `const.py` holds no zone definition. Carry: dismissed: the brief is consumed by this pull request
- carry-audit: contradiction: `tools/audit/carry_audit.py`'s `GROUP_TOK` (`\A[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\Z`) refuses every roster group id with a lower-case tail, so `Carry: R11-SEAM-learners`, the live group this brief lists as a valid target, reads UNROUTED, and the upper-cased spelling reads BAD-DEST. Carry: dismissed: tooling owned by the orchestrator, reported in the seat result





