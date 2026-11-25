# Class sweep: N-staleness (round 11, PLAN phase D, box SW2)

Class mechanism (`dev/audit/config/bugclasses.json`): a staleness limit is
shorter than a report-on-change source's legitimate quiet interval, so a valid
unchanged reading is declared stale or unavailable. Ledger status:
`barriered`.

The barrier is `tests/features.py`'s "R10 N-staleness" check (#2683). Since
then the reader applies `const.INPUT_ON_CHANGE_MAX_AGE_MINUTES` to a source it
has never seen re-report (`inputs.age_limit_for` / `source_polls`).

The judged finding D14-s2-01 is about rows of that table kept equal to the
polling limit. The barrier's named list calls them "fails safe", but they
still publish `stale_inputs` and turn the Input Problem binary sensor on.

Worktree: `origin/handoff/audit-r11-register`, with the judge files from
5806e17d7.

## Enumerator (D14 method step 3)

`PYTHONPATH=tests/hastub:custom_components python3 dev/audit/rounds/round11/D14/sweep-N-staleness/enumerate.py`

**Seams**:

- every key of the effective `INPUT_ON_CHANGE_MAX_AGE_MINUTES`, imported so the
  `**INPUT_MAX_AGE_MINUTES` merge resolves;
- every module-level `*_MAX_AGE_MINUTES` constant in the package, read by AST,
  except the quiet-store anchor and the two tables themselves.

A seam is **FLAG** when limit < QUIET[name]. QUIET is round 10's table of
legitimate quiet intervals, plus the keys added since (heat energy, house
power, thermal power, indoor humidity). A key with no QUIET entry is flagged
`unknown`, so a new source cannot pass unread.

Output: `enumerate.out`, **31 seams, 13 flagged**.

Round 10's enumerator read the polling table. That is no longer the limit a
quiet push source meets, which is why this enumerator reads the on-change
table.

Controls (`controls.out`):

- **positive**: all six D14-s2-01 pump flags are flagged (6/6).
- **null**: a clean on-change table (indoor 360, outdoor 180, power inf) flags
  0.
- **perturbation**: one line restoring the pre-#2683 power row (30 min) flags
  1.

### Probe

`probe.py CONF_KEY` generalises D14-s2-01's `staleness_flags.py` to one key.

- **Setup**: fresh indoor and outdoor, and KEY's entity holding a quiet value
  for 255 min as a report-on-change source (`last_reported` None). One real
  `_update_current_state` + `_build_data_dict`.
- **rc=1** when KEY is published in `stale_inputs`. Every rc=1 also turned
  `InputHealthBinarySensor.is_on` on.
- **Arms**: `--held 10` (null) and `--perturb inf` (the key's on-change limit
  set to inf).

Results (`probe.out`): rc=1 on 7 keys, and every null and perturbation arm
gives rc=0. `staleness_flags.out` re-runs the finding's harness: quiet 6 / Input
Problem 1; null and polled 0; under `--perturb inf` 0 / 0.

## Disposition of every flagged seam (method step 4)

| seam | limit / quiet (min) | disposition |
|---|---|---|
| CONF_HEAT_PUMP_FAULT / DEFROST / ONLINE / BACKUP_HEATER / DHW_BOOSTER / CAPACITY_LIMITED (6) | 30-60 / inf | **instance**, D14-s2-01's judged sites; probe rc=1 each, Input Problem on. |
| CONF_SOLAR_RADIATION_ENTITY | 90 / inf | **instance, beyond the finding.** A push-mode irradiance sensor holds 0 W/m² through every night, which is a 12 h+ quiet interval. Held 255 min, it is published in `stale_inputs` and turns Input Problem on: probe rc=1, null and perturbation 0. It is the same reader consequence D14-s2-01 names. Round 10 dispositioned this row guarded on its control consequence only, and the barrier's named-equal list carries it with that reason. |
| CONF_VALVE_OUTLET_TEMP, CONF_WOOD_TANK_TOP, CONF_WOOD_TANK_BOTTOM, CONF_EXTERNAL_HEAT | 60 / inf | **guarded.** They are read through a local `InputReader` (coordinator.py:5199-5212, :6743; external heat :5154) whose readings never reach the cycle's `InputHealth`. A stale reading therefore never reaches `stale_inputs`. Staleness maps to absence, which the code documents as the intended direction (a stalled hot probe must not read as an indefinite free fire). Probe rc=0. The probe ran without the wood-furnace option, so the 0 comes from the code trace rather than from exercising the wood path. |
| CONF_PV_PRODUCTION_ENTITY | 30 / inf | not applicable: no read site applies the limit (as in round 10); probe rc=0. |
| MODE_LAST_GOOD_MAX_AGE_MINUTES | 180 / inf | not applicable as its own seam: it bounds the last recognised mode's fallback once the mode entity stops being readable. The mode key's own on-change limit is inf. |

The 18 unflagged seams have limit >= quiet. That includes the R10 instances
(power, energy, mode, supply, return, flow, humidity) now at inf or the
quiet-store bound, and coordinator.py `DHW_INLET_MAX_AGE_MINUTES` (1440 /
720). `coordinator.HUMIDITY_MAX_AGE_MINUTES`, a round-10 instance, no longer
exists: humidity reads through the on-change table at 360.

**Count: 7 instances: 6 judged sites and 1 beyond the finding** (solar
radiation).

## Proposed barrier

Extend the existing `tests/features.py` census with the reader consequence the
finding names: for every key the named-equal list keeps, drive it quiet past
its limit through `_update_current_state` + `_build_data_dict`, and require
that it is absent from `stale_inputs`, or that the list names a reason that
covers the published Input Problem (not only the control path). This
enumerator's QUIET table, with its `unknown` flag, also refuses a new key that
is added with no quiet interval. The cost is about 13 keys at roughly 0.3 s
each.
