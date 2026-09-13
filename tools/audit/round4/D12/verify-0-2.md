# D12-01 verification — seat 2 (verifier 2 of 3, re-run)

Worktree `../audit-r4-verify-D12-2`, detached at `0855277edc49cb3cce3b1095fa1e5edcda7663c8`
(branch head; the finding was measured at `7dd68dd`). `git diff --stat
7dd68dd..0855277` over `inputs.py`, `coordinator.py`, `const.py`, `sensor.py`
is **empty**, so the accused code is byte-identical between the baseline and
this tree; exact reproduction below is expected and observed.
Every number here is a count or a published value; `thread_factor=1.0`
quoted per harness. Interpreter
`/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
`PYTHONPATH=tests/hastub:tools/audit/round4/D12`, run from the worktree root
(harnesses copied in-tree per the README rule; `units.py` and `d12lib.py`
resolve the root via `os.getcwd()`/`sys.path.insert`, so they measure this
tree).

## 1. Re-run of the finder's harness (`units.py`)

Base, `--convert`, `--shrink`: **all three reproduce exactly**, at `load1`
4.4–5.2:

| RESULT | finder (7dd68dd) | mine (0855277) |
|---|---|---|
| celsius_inputs_misread (null control) | 0 | 0 |
| imperial_inputs_misread | 10 | 10 |
| imperial_indoor_temperature_c | 70.5 | 70.5 |
| imperial_plan_kwh / steps | 0.0 / 96 | 0.0 / 96 |
| celsius_plan_kwh / steps | 4.752 / 96 | 4.752 / 96 |
| `--convert` imperial_inputs_misread | 10 → 1 | 10 → 1 |
| `--convert` imperial_plan_kwh | 0.0 → 4.198 | 0.0 → 4.198 |
| `--convert` imperial_indoor | 21.389 | 21.38888888888889 |
| `--shrink` imperial_inputs_misread | 10 → 4 | 10 → 4 |
| `--shrink` celsius_inputs_misread | 0 | 0 |

Production mechanics re-read directly: `inputs.py:452-476` `InputReader.read`
is `float(raw_state)` with no unit consultation; `read_power_kw`
(`inputs.py:559`) is the only converting read, through `normalize_power_kw`
(`inputs.py:179-193`), whose docstring states the principle the finding
invokes ("a wrongly scaled power value is worse than no power value"); the
only "Fahrenheit" in production is the `sensor.py:2234` comment recording
the earlier °F household (output side fixed, input side not). All as
claimed.

## 2. My own harness, my own metric

`v2_units_verify.py` (this directory, uncommitted). I do **not** wrap
`InputReader.read`; the number comes from the coordinator's own adopted and
published state, the service-call log and the issue list.

Metric (one line): *for the same physical **minimal** plant (indoor
21.4 °C, outdoor −3.0 °C, DHW tank 52.0 °C, a wired on/off switch — three
sensors, not the 31-slot reference plant), driven through the real
coordinator cycle incl. `_apply_action`: |adopted indoor − 21.4| in K,
planned kWh over the published schedule, switch service commands issued,
repair issues raised, entities unavailable — °C states vs the identical
plant with every sensor natively in °F.*

```
RESULT celsius_indoor_error_k=0.0 K            imperial_indoor_error_k=49.1 K
RESULT celsius_plan_kwh=20.692 kWh             imperial_plan_kwh=0.0 kWh
RESULT celsius_plan_steps=96 count             imperial_plan_steps=96 count
RESULT celsius_max_step_kw=5.0 kW              imperial_max_step_kw=0.0 kW
RESULT celsius_solve_status=None               imperial_solve_status=None
RESULT celsius_switch_off_commands=0           imperial_switch_off_commands=1
RESULT celsius_switch_on_commands=1            imperial_switch_on_commands=0
RESULT celsius_repair_issues=0                 imperial_repair_issues=0
RESULT celsius_sensor_unavailable=17           imperial_sensor_unavailable=17
RESULT thread_factor=1.0  load1=4.43  swapins=0
```

`solve_status=None` is the documented success return
(`coordinator.py:4349` docstring: `None` = solve ran to completion; reason
codes like `"no_prices"` are the refusals) — so the imperial arm is *not*
refused. The 17 unavailable sensors are the plant parts this minimal config
omits, **identical in both arms** — no entity signals the unit error.
Comparison of my metric with the finder's: theirs counts reads whose
adopted unit mismatches the entity's declared unit; mine measures the
end-to-end consequence (adopted-value error, plan energy, actuation,
repairs). They are complements, not the same number; both move only in the
°F arm.

The switch row is a **new datum the finder only inferred**:
`_apply_action` (`coordinator.py:6272`, the `heat_pump_switch_entity` path
at ~6305) really issues `switch.turn_off` in the imperial arm where the °C
control issues `turn_on`. The critical sub-case (a switch-wired install:
pump commanded off, silently, with −3 °C outside) is executed, not argued.

## 3. Attacks and outcomes

**Reachability in real Home Assistant — attacked, could not refute;
strengthened.** Two independent doors. (a) Native-°F hardware: most US-market
thermometers/thermostats publish native °F; the state machine then holds
`"70.5"` with `unit_of_measurement "°F"`, exactly what the harness feeds.
(b) HA's own conversion: the official sensor-entity documentation
(developers.home-assistant.io/docs/core/entity/sensor) states that for a
`device_class: temperature` sensor "the sensor's unit_of_measurement will be
the preferred temperature unit configured by the user" and "the sensor's
state will be the native_value after an optional unit conversion" — on a
US-customary instance **every** temperature sensor with a device class is
exposed in the state machine in °F, whatever the source integration
publishes natively. `InputReader` reads `hass.states.get(...).state` — the
same surface — and `FakeState` models exactly `state.state` +
`attributes["unit_of_measurement"]`, so the stub is faithful here; this is
not a FakeHass-only path. The config flow nowhere requires °C (field
descriptions say only "Indoor temperature sensor"; the °C sliders are the
comfort band, not the entities), so no documented constraint mitigates it.
The same mechanism that fixed the output side for the `sensor.py:2234`
household is what guarantees °F on the input side.

**Null control — sound.** The °C arm of the same plant: 0 misreads, 0 K
error, non-zero plan, `turn_on`. Holds under `--shrink` (reproduced 0).
Causation is isolated by the `--convert` perturbation (10→1 reads, plan
0.0→4.198 kWh, reproduced) and by my arm differential (20.692→0.0 kWh,
`turn_on`→`turn_off`): the unit is the operative variable.

**Grid artefact — attacked and killed.** The failure does not need the
fully-mapped 31-slot reference plant; my minimal 3-sensor install hits it,
with a larger plan delta (20.7 → 0.0 kWh).

**Counting artefact — checked, honest.** The 10 is a count of *reads*, not
entities: 9 distinct entities, with `wood_tank_top_entity` read twice
(`coordinator.py:3247` external-heat observation and `:5026` two-tank
model) — 13 guarded reads total, 8 temperature entities + the Wh energy
meter. The finder's printed list (9 rows) is the deduplicated view of the
same multiset. The Wh row is a second unit family, disclosed by the finder,
and hits metric users too.

**"No repair" — checked structurally.** The only `async_create_issue` calls
in the package are the two setpoint-consistency families in
`setpoint_check.py`; nothing unit-related exists to fire, and my harness
measured `repair_issues=0` in the imperial arm.

**Severity — earned.** Wrong-unit readings pass every `reading_ok` gate (a
real reading, merely in the wrong unit), the plan publishes 96 zero-power
steps, statistics record wrong-scale temperatures, and with a switch wired
the pump is commanded off. The finder scored high rather than critical
because an install without a switch/ECL110 surface keeps the pump's own
curve; my executed `turn_off` confirms the switch-wired sub-case behaves as
they said it would. High is the right panel severity; the critical
sub-class is real and already flagged.

**Contention/timing — not applicable**: all numbers are counts and
published values.

## 4. Nits (non-weakening)

- The finder's statistics sentence ("writes long-term statistics for
  70.5 °C") is right in substance; on a US-customary instance HA would
  display/record that sensor in °F after its own output-side conversion —
  the wrong scale either way. Not load-bearing.
- The finder's harness counts `heat_pump_energy_entity` (Wh) inside
  `imperial_inputs_misread` although it is unit-system-independent;
  disclosed, and it does not inflate the temperature core of the claim
  (8 entities, all adopted unconverted).

## 5. Vote

**verify**, severity **high** (unchanged). My number: on a minimal 3-sensor
plant with a wired switch, the native-°F arm adopts indoor at
**49.1 K** error and plans **0.0 kWh over 96 steps** (control 20.692 kWh,
`turn_on`), with `solve_status=None` (success), **0 repair issues** and an
unavailable-entity set identical to the control — plus **1 executed
`switch.turn_off`**.
