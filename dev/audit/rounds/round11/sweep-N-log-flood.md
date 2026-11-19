# Class sweep: N-log-flood (round 11, PLAN phase D)

Class status in `dev/audit/config/bugclasses.json`: `barriered` (tests/entities.py
check "R10 N-log-flood barrier", enumerator `_r10_unlatched_logs`, latch
`log_latch.log_held`). Mechanism: a persisting condition is logged at WARNING
on every cycle instead of once per transition.

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep_logflood.py` applies the R10 barrier
rule to every WARNING-or-above emitter: `.warning`, `.error`, `.exception`,
`.critical`, and `.log` at a level other than DEBUG or INFO, through any
`getLogger` alias. It reads all 96 package modules. The widening follows
D14-s2-03's seam rule.

Run at `handoff/audit-r11-register` (28b864af6d): R10 (narrow) sites 71, wide
sites 72, beyond the barrier 1.

- Positive control: four planted sites (exception, critical, log(WARNING), an
  alias), D14-s2-03's shape, are found 4 of 4. `coordinator._async_update_data`,
  the D1-s3-06 site, is listed.
- Null control: a latched `.exception` plus INFO/DEBUG calls gives 0.
- Perturbation: adding one unlatched `_LOGGER.exception` line moves it 0 -> 1.

## Dispositions

| seam | disposition |
|---|---|
| `coordinator.py` `_async_update_data`, the generic `except` that logs ERROR with exc_info on every refresh | instance, the judged site of D1-s3-06. Probe: `D1/s3/log_flood.py`. The R10 allow-list files this site as "one record per failed call". That holds for a transient exception, but a persisting exception floods the log. |
| `tests/entities.py` `_r10_unlatched_logs`, which reads only `.warning`/`.error` on the literal `_LOGGER` | instance, the judged site of D14-s2-03. Probe: `D14/s2/logflood_shape.py` |
| `coordinator.py` `_async_first_refresh_light`, the same ERROR arm | not applicable: it runs once at setup, not on every cycle |
| `sysid.py` `_finish` (`.exception`), the one site beyond the barrier | guarded: the sysid state machine reaches it once per finished identification experiment and discards the armed night, so it never runs per cycle |
| the other 69 narrow sites | guarded by the R10 reasoned list (`_R10_LOG_ALLOWED_BY_REASON`), which the barrier pins at exact counts. No count mismatches at this commit |

Instances beyond the findings: 0.

## Proposed barrier change

- Widen `_r10_unlatched_logs` to the wide rule above. It is the same AST walk,
  costing under 1 s of gate time.
- List `sysid._finish` under the once-per-event reason.
- Route the generic arm of `_async_update_data` through `log_latch.log_held`,
  keyed on the exception type, and remove it from the "per failed call" reason.
