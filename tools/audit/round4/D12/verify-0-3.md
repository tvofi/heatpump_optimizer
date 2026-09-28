# D12 verifier 3 — finding D12-01 (round 4, panel D12-0)

Tree: worktree `audit-r4-verify-D12-3` at `0855277` (branch head). The
finding's baseline `7dd68dd` differs from the head by nothing in
`inputs.py` or `coordinator.py` (`git diff --stat 7dd68dd 0855277 -- ...
inputs.py coordinator.py` is empty), so the reproduction is at the same
code that was measured. Every number below is a count, a share or a
published value — no timing, `thread_factor=1.0`, `load1` 2.9–3.1 quoted
per block, box shared (irrelevant to counts).

## 1. Re-run of the finder's harness (exact)

`PYTHONPATH=tests/hastub:tools/audit/round4/D12 python3
tools/audit/round4/D12/units.py` — run from the worktree root; `d12lib`
inserts `os.getcwd()`-relative paths, so it measures the tree it is run
from (the worktree, per the README's root-rule warning; I confirmed the
`custom_components` it imported is the worktree's).

| quantity | finder | my re-run |
|---|---|---|
| celsius_inputs_misread (null control) | 0 | **0** |
| imperial_inputs_misread | 10 | **10** |
| imperial_indoor_temperature_c | 70.5 | **70.5** |
| imperial_dhw_temperature_c | 125.6 | **125.6** |
| imperial_outdoor_temperature_c | 26.6 | **26.6** |
| imperial_plan_kwh / steps | 0.0 / 96 | **0.0 / 96** |
| celsius_plan_kwh / steps | 4.752 / 96 | **4.752 / 96** |
| `--convert` misread / indoor / plan | 1 / 21.39 / 4.198 | **1 / 21.389 / 4.198** |
| `--shrink` misread / celsius control / plan | 4 / 0 / 0.0 | **4 / 0 / 0.0** |

Exact to the last digit on every count and published value, all three
invocations. (`load1` 3.01 / 2.92 / 3.02; the misread roster lists 9
distinct entities because `wood_tank_top_entity` is read twice — external
heat observation and two-tank seed — so 10 reads over 9 entities + the Wh
meter.)

## 2. My own harness (independent metric, independent instrumentation)

`tools/audit/round4/D12/verify-0-3-units.py` — written for this seat. It
does **not** wrap `InputReader.read`; it drives the coordinator's real
`_update_current_state()` / `async_run_optimization()` /
`_build_data_dict()` and the sensor platform's real `async_setup_entry`,
and measures the adopted temperatures from `coord._current_state`, the
plan from the published schedule, and the published sensor values from
the entities themselves. Three arms: °C control; °F states with
`unit_of_measurement: "°F"` (what a US-customary state machine holds);
and the same °F plant **converted in the fixture** — my perturbation is
in the states, not a monkeypatch of production, so it is independent of
the finder's `--convert` too.

My metric definition: *absolute error of the coordinator's adopted
indoor/DHW/outdoor temperature (°C) on the °F plant, the share of the 96
schedule steps commanding zero compressor power, the count of steps whose
`heat_pump_on` flag is False, and the sensor platform's published
`indoor_temp` value — °F arm against the °C control and against the
fixture-converted arm.*

```
RESULT celsius_indoor_error_c=0.0      fahrenheit_indoor_error_c=49.1   converted_indoor_error_c=-0.011
RESULT celsius_dhw_error_c=0.0         fahrenheit_dhw_error_c=73.6      converted_dhw_error_c=0.0
RESULT celsius_outdoor_error_c=0.0     fahrenheit_outdoor_error_c=29.6  converted_outdoor_error_c=0.0
RESULT celsius_zero_power_share=0.8958 fahrenheit_zero_power_share=1.0  converted_zero_power_share=0.8854
RESULT celsius_pump_off_steps=76       fahrenheit_pump_off_steps=96     converted_pump_off_steps=75
RESULT celsius_plan_kwh=7.151          fahrenheit_plan_kwh=0.0          converted_plan_kwh=9.108
RESULT celsius_published_indoor_c=21.4 fahrenheit_published_indoor_c=70.5 converted_published_indoor_c=21.4
RESULT fahrenheit_solve_status=None reason_code   (None = ran to completion: no refusal)
RESULT fahrenheit_sensor_unavailable=8 count (the SAME 8 as the celsius arm: not unit-driven)
RESULT fahrenheit_sensor_setup_crash=None
```

(My °C plan is 7.151 kWh where the finder's is 4.752: my driver injects a
zero solar curve where theirs injects a diurnal one. Different drivers,
same invariant: the °F arm is the only one at a 1.0 zero-power share.
`converted_indoor_error_c=-0.011` is the double rounding of my own
fixture conversion, inside the stated ±0.05.) The definitions are
comparable: the finder's count of misadopted reads and my error magnitudes
are the same mechanism measured two ways, and both swing to ~0 under a
conversion.

## 3. Attacks

**A. Is a non-metric instance reachable in real HA — or is the °F state
machine a stub fantasy?** The strongest available attack, and it fails to
refute. Home Assistant's own developer docs (Sensor entity) and the 2021
"temperature conversions moving to SensorEntity" blog: a sensor with
`device_class: temperature` is auto-converted **to the instance unit
system** — and the converted value is what lands in the state machine, not
a display layer. On a US-customary instance the state machine therefore
holds °F (natively-°F hardware stays °F; °C-native hardware is converted
to °F by HA itself). A second, unit-system-independent door: sensors
without a device class (common in MQTT and template configurations) are
never converted on any instance, so a bare °F probe reaches the bug even
on a metric install. Either way `hass.states.get(id).state` is a °F
number and `InputReader.read` is `float(state.state)` with no unit
consultation (`inputs.py:452-474`), while the sibling `read_power_kw`
(`inputs.py:559`) and `_pv_measured_production` (`coordinator.py:8552`)
do consult `unit_of_measurement` through `normalize_power_kw`, whose
docstring states the exact principle the temperature path violates.
`sensor.py:2234`'s comment records a real Fahrenheit household already
reported — the output side got `device_class: TEMPERATURE`, the input
side got nothing. Reachable, on both doors.

**B. Stub artefact?** No. Nothing in the measurement leans on FakeHass
executor serialisation or coroutine closing — the accused line is a
synchronous `float(state.state)` that runs identically against a real
`State`. The spy consults `attributes["unit_of_measurement"]`, a plain
dict lookup on real HA states too.

**C. Null control.** Sound. The °C arm is the same plant, same driver,
same injection; 0 misreads and a sane plan in every run (mine and the
finder's), and it holds under `--shrink` (0 at both plant sizes). Under
real HA semantics the metric arm is even safer than the harness implies.

**D. Grid artefact / inflated count?** Not an aggregate — one cell, two
arms; `--shrink` moves 10 → 4 with the plant. If anything the count is
conservative: `wood_tank_bottom_entity` is read bare in production
(`coordinator.py:3248, 5027`) but carries no unit in the fixture (default
state `"0"`), so it is not counted; a real °F wood-bottom probe would
make it 11. Likewise the Wh energy read (`coordinator.py:4988`, bare
`reader.read`) is unit-system-independent — a Wh meter on any instance,
metric or not, is adopted as kWh (1000× error), which widens rather than
narrows the class.

**E. Is "0.0 kWh, no refusal, no repair, no unavailable" real?** Measured
it myself: `solve_status=None` (the code documents None as "ran to
completion"; reason codes `no_prices`/`solve_failed` exist and did not
fire), 96 steps published, every step `heat_pump_on=False`, the same 8
sensors unavailable as on the °C arm (pre-existing), no setup crash, and
the repair issue the tree does have (`solve_failures`) is created only
after repeated solve *failures* — a successful all-zero solve raises
nothing. The published `indoor_temp` sensor reads 70.5 °C.

**F. Severity.** Earned, and the finder's own downgrade to high is the
right call. With a switch wired, `_apply_action` (`coordinator.py:6272`)
actuates the plan: my `fahrenheit_pump_off_steps=96` means
`switch.turn_off` on every step of the horizon — that arm is arguably
critical (silent loss of heat in winter, nothing in the UI says why). But
actuation is conditional on a wired switch/ECL110/climate surface; a user
who wired none keeps the pump's own weather curve and loses the
optimization, not the heat. The finder states exactly this. High is the
defensible score.

## 4. Vote

**verify**, severity **high** (as filed). The claim's production-code
reading is accurate at every citation I checked (`inputs.py:452`,
`inputs.py:559`, `inputs.py:179`/`const.py:122` and its docstring,
`coordinator.py:3246-3248/4915-5030`, `sensor.py:2234`); the harness
reproduces exactly; my own harness with my own metric and a
fixture-side perturbation reproduces the mechanism, the magnitude
(+49.1 °C indoors, 125.6 °C tank, 26.6 °C outdoors for −3.0), the silent
96-step all-off plan and the 70.5 °C published sensor; the reachability
attack against real HA confirms rather than breaks the premise; the null
control holds everywhere it was re-taken.

My metric definition (one line): *absolute error of the adopted indoor
temperature (°C) and the share of 96 published steps commanding zero
power, °F-arm plant against the °C control and a fixture-converted arm.*
