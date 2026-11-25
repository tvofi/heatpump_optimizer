# Class sweep: N-stale-step-actuation (round 11, PLAN phase D, box SW2)

Class mechanism (judge, D16-s2-01/02): an actuator is commanded from the
previous solve or step, so it holds or switches one interval late against the
plan it serves.

- Nearest existing class: N-no-expiry. That class is about a value's age; this
  one is a timing offset, a fresh value applied to the wrong step.
- `dev/audit/config/bugclasses.json` has no entry for this class yet: it is
  new this round, with no detector and no barrier (`barriered: false`).

Worktree: `origin/handoff/audit-r11-register`, with the judge files from
5806e17d7.

## Enumerator (D14 method step 3)

`python3 dev/audit/rounds/round11/D14/sweep-N-stale-step-actuation/enumerate.py`
reads the package by AST.

- **Cut-action read**: an access to `_current_action` (written once per solve,
  coordinator.py:4120), `self._action()` (legionella's view of it), or
  `get_current_action(...)`. Getters count as reads too, to a fixed point:
  functions that read the cut and reach no write, such as
  `_commanded_split` -> `_commanded_power`.
- **Actuator write**: `async_call`, `async_publish`/`publish`,
  `select_option`, `set_value`, `write_setpoint`, `_async_set_pump`,
  `switch_supply`, `_drive_switch`, `turn_on`/`turn_off`. A function reaches
  one directly or through the name-resolved call graph.
- **Seam**: a function that does a cut-action read and reaches an actuator
  write. `step_keyed` marks a function that calls `_step_index` itself.
- **Output**: `enumerate.out`, **19 seams**. The seam rules of both findings
  start the list and are all covered.

Controls (`--controls`, output in `controls.out`):

- **positive**: finds every finding site: `_command_frequency` and
  `async_publish_current_action` (D16-s2-01), `async_track_cycle` (D16-s2-02).
- **null**: a clean fixture that writes `plan.freq[_step_index(plan, now)]`
  and reads `_current_action` only into a payload gives seams=0.
- **perturbation**: replacing the step lookup with one line reading
  `self._current_action` moves the count 0 -> 1.

## Probes

- `D16/s2/timing.py`, re-run here (`timing.out`), reproduces the finding
  exactly:
  - stale share mqtt displace 0.5732, curve offset 0.4644, frequency 0.4480;
  - supply, mode, flow class and space pump all 0 (906-1434 graded minutes).
- `D16/s2/disinfect.py`, re-run here (`disinfect.out`): on in window 0 of 30,
  on outside 30; long window 59 of 90.
- New `probe_peak_guard.py` (`probe_peak_guard.out`), on D16-s2's rig:
  - setup: a plan with step 0 partial (displace 4) and step 1 full (6), cut at
    T0+1 min;
  - at T0+16 min the peak guard engages and releases. The release publishes 4
    where the step's own value is 6: **rc=1**;
  - null: the release at T0+5 min, inside the cut's step, publishes 4 = 4,
    rc=0;
  - perturbation: a cycle re-cut at T0+16 before the release publishes 6,
    rc=0.

## Disposition of every seam (method step 4)

| seam | disposition |
|---|---|
| coordinator.py `_command_frequency` | **instance**, D16-s2-01 site; timing.py frequency 0.4480. It runs only in the cycle tail, with no step re-derivation. |
| coordinator.py `async_publish_current_action`, `async_publish_ecl110_command` | **instance**, D16-s2-01 site (one write path: ECL110 MQTT displace and heat-curve offset); timing.py 0.5732 / 0.4644. |
| legionella.py `async_track_cycle` | **instance**, D16-s2-02 site; disinfect.py on_in_window 0/30. |
| coordinator.py `_async_peak_guard_transition` | **instance, beyond the findings.** A state-listener transition (`_on_power_event`), not the cycle, writes it. Engage publishes the cut `displace_value` minus the nudge, and release re-publishes the cut action, with no step lookup and no `_plan_is_stale` check. A fix that re-derives the step on the cycle path, or on a new step tick, leaves this write one step late. probe_peak_guard.py rc=1. |
| coordinator.py `_command_valve_target` | **D16-s2-01 site by its mechanism** ("the valve hold schedule"): a pre-resolved `valve_target`, written only when a solve runs. D16-s2's rig carries no mixing-valve entity, so no probe here measures it. It is **not listed as an instance** in the JSON, which requires a failing probe; it is left unmeasured. |
| coordinator.py `_apply_action` | Supply switch: **guarded**. `cycle_supply` -> `step_supply` -> `pump_arbiter._step_index(plan, now)`, re-driven on the one-minute supply tick (pump_arbiter.py:2062); stale_share_supply=0. Its ECL110 publish is the D16-s2-01 site above. |
| coordinator.py `_async_drive_pumps` | **guarded**: the space pump's step is indexed from `now` (`plan_commands_heat(schedule, idx)`); stale_share_space_pump=0 of 906. |
| pump_arbiter.py `apply`, `_arbitrate`, `_lead_mode`, `_listen` | **guarded**: the arbiter's one-minute tick (pump_arbiter.py:2168, `_TICK`) re-derives the step via `_step_index(plan, now)` before any mode, silent, night or set-point write; stale_share_mode=0, switch_on_with_wrong_mode=0 of 60. The cut is read only for `mode`/`dhw_reason` tags of the step. |
| pump_arbiter.py `release` | not applicable: unload writes the baseline row, not a plan step. |
| coordinator.py `_fold_measured_cop`, `_async_learn_interval`, `_update_current_state`, `_async_first_refresh_light` | not applicable: the cut read feeds a learner, detection or the model's ECL state, not an actuator. The write the enumerator reaches goes through other calls (legionella, counted above). |
| coordinator.py `_async_update_data` | not applicable as its own seam: no direct read; its write tail is the seams above. |
| coordinator.py `async_run_optimization` | not applicable: it is the cut's writer (`boost.adopt_plan(get_current_action(result, now))`). Its valve write is `_command_valve_target` above. |

**Count: 4 instances listed: 3 judged sites and 1 beyond the findings**
(`_async_peak_guard_transition`). The valve seam is unmeasured.

## Proposed barrier

A static `tests/` arm over this enumerator. Every function that reaches an
actuator write from the cut action must either call `_step_index` (or a named
step re-deriving helper) or be on a reasoned list with its cadence. The arm
runs in under 1 s.

The fix it gates: a one-minute (or step-boundary) re-drive for frequency,
ECL110 displace, curve offset, valve and the disinfection switch, keyed on
`_step_index(plan, now)`. The peak-guard path must read the same re-derived
step.
