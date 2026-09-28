# Sweep: "CPU work inline on the event loop"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Findings: D9-s1-03
(verified, low), D9-s2-01 (verified, low). Not a ledger class (new).

## Enumerator

`enumerate.py` re-runs both findings' own seam_rules and widens the second
to every `simulate_step`/`rank_sensor_advisor` call in `sensor.py`/`topology.py`.

```
$ python3 tools/audit/round9/D14/sweep/cpu_work_inline_event_loop/enumerate.py
RESULT candidate_sites=6
```

## Positive control

- `coordinator.py:10478` (`_sysid.arm`) and `:10512` (`_sysid.step`), called
  from `_run_system_identification` (coordinator.py:10487), itself called
  directly (no `hass.async_add_executor_job`) at `coordinator.py:5079` inside
  `_async_update_data` — confirmed by `grep -n "_run_in_process\|async_add_executor_job\|_run_system_identification" coordinator.py`:
  only `_run_in_process`/optimizer calls route through the executor; sysid
  does not.
- `sensor.py:111` (`_sensor_advisor_attribute`), called from a sensor
  entity's `extra_state_attributes` property (HA reads properties
  synchronously on the event loop by construction; there is no executor
  route for a property getter), which calls `topology.rank_sensor_advisor`,
  which runs `ThermalModel.simulate_step` in a loop (`topology.py:850`) once
  per unconfigured optional sensor candidate x2 band edges.

Both sites are present at baseline `1936d5ca` and unchanged on `origin/main`
(`git diff 1936d5ca..origin/main -- custom_components/heatpump_optimizer/{coordinator,sensor,topology}.py`
touches only `coordinator.py`'s unrelated `async_reset_comfort_weight`, not
these lines).

## Null control

Every other `extra_state_attributes` property in `sensor.py` (8 further
sites at the enumerator's grep) either returns a precomputed dict field from
`coordinator.data` or a cheap formatting call — none call `simulate_step` or
`rank_sensor_advisor` — so the widened grep does not over-count.

## Perturbation

Both existing findings already carry an executed number and a moved
perturbation (D9-s1-03: 43-228 ms measured in-process; D9-s2-01:
`loop_simulate_steps_per_read` moves from a fallback path). The sweep does
not re-run the heavy quiet-window timing per tvofi's no-heavy-D3/D9-rerun
rule; it reuses the finder's own evidence (`tools/audit/round9/D9/s1/` and
`s2/`, evidence branch `handoff/audit-r9-evidence`).

## Disposition

| seam | disposition |
|---|---|
| coordinator.py:10478, :10512 (`_sysid.arm`/`.step` via `_run_system_identification`) | instance — D9-s1-03 |
| sensor.py:111 -> topology.py:850 (`rank_sensor_advisor` -> `simulate_step`) | instance — D9-s2-01 |
| topology.py:891 (`rank_sensor_advisor` def) | not applicable — definition site, not a call site |
| topology.py:902 (docstring mention) | not applicable — comment, not code |

## Count

N = 2 verified findings + 0 sweep-confirmed instances = **2**. N < 3 and the
class is not ledger-barriered, so **rca: false**, matching the brief.

## Barrier proposal

None proposed by the sweep (N < 3); the finders' own reports already name a
scope (route both through `hass.async_add_executor_job`, or precompute
`sensor_advisor` once per cycle in `_async_update_data` rather than per
attribute read) for the fixer to pick up.

## Gate seconds

~0.05s (two `grep` invocations).
