# Class sweep: N-stale-step-actuation (round 11, D14 steps 3-4)

**Mechanism:** an actuator is commanded from the previous solve or step, so it holds or switches one interval late against the plan it serves.
**Findings in the class:** D16-s2-01 (frequency, ECL110 MQTT displace and heat-curve offset), D16-s2-02 (disinfection switch).
**Ledger status:** `dev/audit/config/bugclasses.json` has no `N-stale-step-actuation` key at `handoff/audit-r11-register` (28b864af6d). The class is new from the judge and is not yet registered, so it has no detector and no barrier. Registering it belongs to the fold.

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep_stale_step.py custom_components/heatpump_optimizer`

The enumerator is an AST walk over the whole package. It returns a seam for any function that reads the solve-cut action (`_current_action`, `self._action()` or the `planned()` closure) and writes to an actuator, either in its own body or through a same-module callee. It also returns a seam for any function that writes directly with a value a same-module callee read from the action (this is how `_command_frequency` reaches `_commanded_split`). A cross-module pass then adds functions in other modules that call a flagged writer. Write verbs: `async_call`, `publish`, `turn_on`/`turn_off`, `_drive_switch`, `write_displace`, `publish_ecl110_topics`, `async_publish_*`, `_command_valve_target`, `async_set_value`, `_valve_write_problem`.

| control | command | result |
|---|---|---|
| positive | the enumerator on the package | 14 seams, including every finding site: `_command_frequency`, `async_publish_current_action`, `async_publish_ecl110_command` and `_apply_action` (D16-s2-01), and `LegionellaGuard.async_track_cycle` (D16-s2-02) |
| null | `--null` (a fixture where the writer re-indexes the plan at `now`) | COUNT 0 |
| perturbation | `--perturb` (the same fixture plus one cycle writer reading `self._current_action.get("x")`) | COUNT 0 -> 1 |

I re-ran both finder harnesses at this head (`/Users/timmalmstrom/hpo-orch/r10s6/venv-ci`, hastub). `timing.py`: mqtt 0.5732, curve 0.4644, frequency 0.4480; supply, mode, flow_class and space_pump 0. `disinfect.py` was also run. The findings reproduce exactly.

## Disposition of every seam

| seam | disposition | reason / probe |
|---|---|---|
| coordinator `_command_frequency` | instance (D16-s2-01) | timing.py frequency 0.4480 |
| coordinator `async_publish_current_action` | instance (D16-s2-01) | timing.py curve 0.4644 |
| coordinator `async_publish_ecl110_command` | instance (D16-s2-01) | timing.py mqtt 0.5732 |
| coordinator `_apply_action` | instance (D16-s2-01) | cycle-only driver of the two publishes above |
| legionella `LegionellaGuard.async_track_cycle` | instance (D16-s2-02) | disinfect.py on_in_window 0/30 |
| coordinator `_command_valve_target` | **instance, beyond the findings** | `probe_stale_step.py valve` -> FAIL. It writes the action's `valve_target` (the hold schedule's step entry). Its only caller is `async_run_optimization`, and the coordinator registers no per-step tick, so the valve holds the cut step's target into the next step. D16-s2-01's mechanism text names it, but no metric graded it. |
| coordinator `_async_peak_guard_transition` | **instance, beyond the findings** | `probe_stale_step.py peak_guard` -> FAIL. A meter crossing re-publishes `self._current_action` (nudged on suppress, as-is on release) with no step re-cut, so after a step boundary it writes the previous step's displace and on/off. |
| coordinator `_on_power_event` | not applicable | only the caller that spawns `_async_peak_guard_transition`; counted at that seam |
| coordinator `_update_current_state` | not applicable | its own read feeds the ECL110 lag model with the command that was in force over the elapsed interval, which is the right one. Its write path is `async_observe` -> `async_track_cycle`, counted under D16-s2-02. |
| coordinator `async_run_optimization` | not applicable | the cut site itself. Its writes are the callees listed above. |
| coordinator `_async_drive_pumps` | guarded (measured) | vvc branch: wall-clock DHW windows, not the action. Space branch: indexes the plan at `now` with `heat_now or heat_next` lookahead and writes transitions only. timing.py `stale_share_space_pump=0.0000` (0 of 906 graded minutes). |
| climate `_async_publish_displace_from_current_action` | not applicable | publishes after `publish_then_refresh` has run the new mode's solve, so the action is freshly cut |
| button `async_press` | not applicable | runs a solve; the action is freshly cut |
| services `handle_run_optimization` | not applicable | runs a solve; the action is freshly cut |

Guards the enumerator does not return: `pump_arbiter.supply_tick` (#2492) and the arbiter's one-minute `apply` tick. Both re-derive their step each minute from `plan_step_start(now)` / `step_supply`, which is why supply, mode and flow_class measure 0.

## Count and barrier

There are 7 instances: 5 finding sites and **2 beyond the findings**. The class is unbarriered.

Proposed barrier: run the enumerator as a `tests/` structural check. Every seam it returns must either be on an allow-list naming its guard or not-applicable reason, or be reachable from the step tick. Pure AST, under 1 gate-second.

Recommended for the fix group of D16-s2-01/02: one step-boundary tick (the one that already drives `supply_tick`) re-cuts the action and drives frequency, MQTT, curve, valve, the disinfection switch and the peak-guard republish, each keeping its own rate limit.

## Limits

- The probes for the two beyond-finding seams are static (call graph plus re-cut check), not plant runs.
- The enumerator follows callees within one module only, plus one cross-module caller pass. A writer that reads the action through an object attribute in a third module would be missed.
- The worktree is a sparse checkout (`custom_components/`, `tests/`, D14.md, `bugclasses.json`, the round-11 files). The disk had about 240 MiB free, so a full checkout failed.
