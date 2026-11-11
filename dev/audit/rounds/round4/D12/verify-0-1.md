# D12 verify-0-1 — seat 1 of panel D12-0, round 4 (re-run)

Finding: **D12-01** (high, bug) — `InputReader.read` is `float(state.state)` and
consults no unit, so on a non-metric Home Assistant instance 10 of 13 guarded
inputs are adopted in the entity's own unit; indoor publishes 70.5 °C for a
plant at 21.4 °C; the 96-step plan totals 0.0 kWh with no refusal, no repair,
no unavailable entity. `read_power_kw` is the one read that converts.

Tree under review: `0855277edc49cb3cce3b1095fa1e5edcda7663c8` (branch head,
detached worktree `../audit-r4-verify-D12-1`). Baseline `7dd68dd`. Production
delta vs baseline: `git diff --stat 7dd68dd..HEAD -- custom_components/` =
`manifest.json` and `www/heatpump-optimizer-card.js` version strings 6.4.2 →
6.4.3 only. The Python the finding hooks is byte-identical to baseline.
Machine: MacBookAir10,1, 8-core Apple M1, 8 GB, macOS 26.6 — same physical box
class the finder used (finder quoted macOS 25.6.0). Every number below is a
**count or a published value**; none is a timing. `thread_factor=1.0`,
`swapins=0`, `load1` 2.28–3.24 quoted per block, no `stress.py`/`run.sh`
processes concurrent (checked, count 0).

## 1. Re-run of the finder's harness (`units.py`, header command)

`PYTHONPATH=tests/hastub:tools/audit/round4/D12` + python 3.11, from the
worktree root, exactly as the header says. Root rule: `d12lib` inserts
`os.getcwd()` paths — measures the tree it is run from; I ran it in the
worktree under review.

| run | key RESULTs | finder's value | verdict |
|---|---|---|---|
| default | `celsius_inputs_misread=0`, `celsius_indoor_temperature_c=21.4`, `celsius_plan_kwh=4.752`, `celsius_plan_steps=96`; `imperial_inputs_misread=10`, `imperial_indoor_temperature_c=70.5`, `imperial_dhw_temperature_c=125.6`, `imperial_outdoor_temperature_c=26.6`, `imperial_plan_kwh=0.0`, `imperial_plan_steps=96` | same | exact |
| `--convert` | `imperial_inputs_misread=1` (residual = `heat_pump_energy_entity` Wh), `imperial_indoor_temperature_c=21.389`, `imperial_plan_kwh=4.198` | same | exact |
| `--shrink` | `celsius_inputs_misread=0` (control holds), `imperial_inputs_misread=4`, `imperial_plan_kwh=0.0` | same | exact |

All three runs reproduce the finder's numbers with zero deviation, well inside
the stated tolerance (exact on counts, ±0.1 on °C/kWh). The misread list is the
same 9 distinct keys; the count is 10 because `wood_tank_top_entity` is read
twice (`coordinator.py:3247` external-heat observation and `:5026` two-tank
branch).

## 2. My own harness (`d12_own_01.py`, written beside the finder's)

Different instrument and different metric. The finder counts **read calls**
whose entity unit is non-metric, from a wrapper on `InputReader.read`. I count
**distinct configured slots** whose raw °F/Wh state is found **verbatim among
the coordinator's adopted floats** (published `data` dict walked recursively,
`vars()` of the thermal state and thermal params, the private `_measured_*`
fields) — adoption proven from the coordinator's own state, not from a
read-return log. My harness also drives the six platforms itself (to count
unavailable entities), counts repairs on `hass.issues` (the issue-registry
stub records them), counts zero-power plan steps, and prints the published
indoor sensor's device class.

**Metric definition (one line):** distinct configured input slots publishing a
non-metric `unit_of_measurement` (°F/Wh) whose RAW numeric state appears
verbatim among the values the coordinator adopted after one full cycle, plus
the published plan's total heating kWh / zero-power steps / repairs /
unavailable entities, on one physical plant driven twice (°C arm = null
control).

```
RESULT own_celsius_slots_misadopted=0 count        <- NULL CONTROL
RESULT own_celsius_plan_kwh=4.752 kWh   steps=96  zero_power_steps=91
RESULT own_imperial_slots_misadopted=10 count      (10 pool hits)
RESULT own_imperial_read_calls_misread=10 count    (finder-comparable, same 10)
RESULT own_imperial_indoor_c=70.5 degC
RESULT own_imperial_plan_kwh=0.0 kWh    steps=96  zero_power_steps=95
RESULT own_imperial_solve_status=None             (None = success, no refusal)
RESULT own_imperial_repairs_raised=0 count        (celsius arm: 1, unrelated)
RESULT own_imperial_entities_unavailable=9 count  (celsius arm: 9 — identical)
  indoor sensor indoor_temp: device_class=temperature state_class=measurement
                            value=70.5 available=True
RESULT own_small_imperial_slots_misadopted=4 count   <- independent shrink plant
RESULT own_small_imperial_plan_kwh=0.0 kWh  steps=96 zero_power_steps=96
RESULT own_fix_imperial_slots_misadopted=1 count     <- my --fix arm (see below)
RESULT own_fix_imperial_indoor_c=21.389 degC
RESULT own_fix_imperial_plan_kwh=4.198 kWh  zero_power_steps=91 (= celsius)
RESULT thread_factor=1.0  load1=2.28  swapins=0
```

**False-positive forensics on my own number** (refute-first applied to
myself): of the 10 pool hits on the imperial arm, two are coincidences, not
adoptions — `mixing_valve_write_entity` (95.0) duplicates the valve target's
misadopted value, and `space_setpoint_entity` (69.8) matches a
`dhw_schedule[88]['dhw_temp']` step of 69.8 °C that the plan legitimately
contains. So my adoption-proven distinct count is **8**, plus
`wood_tank_top_entity` (131.0) which my spy proves was handed to the caller
twice unconverted but lands outside my float pool (numpy surface my walker
does not recurse into): **9 distinct slots genuinely misread = the finder's 9
distinct keys, one-for-one.** In the `--fix` arm (my own one-line °F→°C +
Wh→kWk conversion in `InputReader.read`) the single residual hit
(`floor_return_temp_entity` 82.4) is also a coincidence — 82.4 pre-exists in
the **celsius** pool, where floor return is 28.0 °C, i.e. some flow-target
value the plan already contains. Under the fix, indoor returns to 21.389 °C,
the plan returns 4.198 kWh and the zero-power step count returns to the
celsius arm's 91.

Both metric definitions are written down; they agree on every substantive
point (the ±1 is call-count vs distinct-slot over the double wood-top read,
and my pool's two coincident hits are identified above).

## 3. Attacks (verifier contract, in order)

1. **Contention** — not applicable: counts and published values, immune to
   load; `thread_factor=1.0`, `swapins=0`, `load1` 2.28–3.24, zero concurrent
   gate processes.
2. **Wrong gate mode** — n/a; no suite-gap claim, no gate run.
3. **Grid artefact** — not a grid aggregate: one physical plant. Two
   independent plant sizes (finder's 20-key shrink → 4; my minimal 4-slot
   plant → 4, plan 0.0 kWh, 96/96 zero-power steps) both move the count in
   the stated direction.
4. **Null control** — present and holding in every arm: °C arm misadopted 0,
   plan 4.752 kWh. The failure appears only when the same plant speaks °F/Wh.
5. **Stub vs real HA** — `tests/harness.py:FakeState` puts
   `unit_of_measurement` in the state's attributes exactly as HA does and
   `FakeHass.states.get` returns it; the imperial arm is a faithful model of
   a `device_class: temperature` sensor on a US-customary instance (state in
   °F, unit attribute °F). `config_flow.py:1432` accepts any temperature
   sensor for these slots. Reachable in real HA. Production-side there is no
   conversion path anywhere: the only Fahrenheit occurrence in
   `custom_components/` is the comment at `sensor.py:2234` recording that a
   Fahrenheit household was already reported (output side fixed with a
   TEMPERATURE device class; input side untouched). `grep` for
   `TemperatureConverter|unit_system` in production: absent.
6. **Severity earned** — the imperial arm publishes a 96-step plan totalling
   0.0 kWh (95 steps at exactly zero power) while publishing indoor 70.5 °C
   *available* with `device_class=temperature`, `state_class=measurement`
   (HA writes long-term statistics for it), raising **0** repair issues
   (fewer than the celsius arm's 1, which is config-related) and leaving
   unavailable counts identical (9 = 9). No refusal (`solve_status=None`).
   Every reading_ok gate passes because the number is a real reading in the
   wrong unit, exactly as claimed. The finder's self-discount from critical
   to high (loss of optimisation vs loss of heat depending on whether a
   switch/ECL110 surface is wired) is sound; I keep **high**.

## 4. Incidental

My harness surfaced the same bare-`float(state.state)` mechanism on a path
the finder's count does not reach: `coordinator.py:2139` reads
`CONF_DHW_INLET_ENTITY` raw with a −5.0..35.0 plausibility band that a °F
value inside the band passes (48.2 °F for 9.0 °C) — same bug family, read
lazily, not counted by either harness.

## 5. Vote

**verify**, severity **high** (finder's). My number: 9 distinct slots
misadopted (adoption-proven 8 + read-proven wood_top; the finder's 10 counts
the double wood-top read), indoor published 70.5 °C, plan 0.0 kWh / 96 steps
/ 95 zero-power steps, 0 repairs, 0 delta unavailable; °C control 0 / 21.4 /
4.752; fix → 0 genuine residuals and 4.198 kWh; independent small plant → 4
/ 0.0 kWh.
