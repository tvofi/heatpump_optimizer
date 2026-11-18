# D12 verification: round 8, seat D12-v1 (single verifier)

Tree: /home/claude/audit-r8/seats/D12-v1 (copy tree, baseline cdf82daa). The finder's evidence was copied from seats/D12-s1. No harness hard-codes a seat path, so none needed rewriting. Every run used PYTHONPATH=tests/hastub, the five BLAS variables set to 1, and TMPDIR/HPO_PLANDATA under /home/claude/audit-r8/tmp/D12-v1. All counts are exact. No timing number is quoted. thread_factor was 1.000 on every run. `diff -rq` against the export shows no production file changed.

## D12-s1-01: the heat-pump switch slot accepts input_boolean and climate, but `_apply_action` always calls `switch.*`

**Finder's harness, re-run** (`s1_actuation.py`):

| arm | unroutable_writes | surfaces_unactuated | null (switch) | load1 |
|---|---|---|---|---|
| baseline | 2 | 2 | 0 | 4.54 |
| `--fix-arm` ("switch" changed to "homeassistant") | 0 | 0 | 0 | 5.21 |

Both arms match the finder exactly. `assign_entity` accepted both entities (`assign=True`), and a plan was published in every row.

**My own harness** (`v1_switch_follow.py`).

- **Metric:** over every domain that `topology.ASSIGNABLE_KEYS[heat_pump_switch_entity]` accepts, read from production (switch, input_boolean, climate), and both initial entity states, I count the runs in which the entity's state after one cycle does not match `_current_action["heat_pump_on"]`.
- **Routing model:** an emulation of Home Assistant entity-service routing. A `<d>.turn_*` call acts only on `<d>.*` entities. A `homeassistant.turn_*` call dispatches by the entity's own domain.
- **Differences from the finder's harness:** the coordinator is built bare, the slot is filled through entry options rather than the service, and the key is the entity's resulting state rather than the domain pair.

Results:
- **Baseline:** not_following_runs = **2 of 6** (input_boolean and climate, each starting "on", commanded off, still on/heat afterwards). Null control (switch): 0. load1 3.83.
- **My own perturbation**, a different one-line fix (`"switch"` changed to `switch_entity.split(".")[0]`): **0 of 6**. load1 3.81.

**Attacks on the method:**
- **Contention:** none. Every metric is a count.
- **Gate mode:** not applicable. This is not a claim that the test suite misses something.
- **Grid artefact:** each surface or domain is an independent binary. Dropping any one cell changes the count by at most 1, and the null row is always 0.
- **Null control:** present and passing in both harnesses.
- **Reachable in real Home Assistant?**
  - The code is `coordinator.py:6631`, which calls `"switch"` with a fixed domain. `topology.py:129-130` accepts `("switch", "input_boolean", "climate")`. `services.py:600` validates against that tuple. The card picker (`heatpump-optimizer-card.js:9192-9219`) filters candidates by the same slot domains, so a user can pick these entities by clicking in the UI.
  - The config flow and options flow (`config_flow.py:1257`, `:1514`) offer `switch` only. So the only way to reach the bug is the diagram's click-to-assign, or calling the service directly.
  - In real Home Assistant, `switch.turn_off` with an `input_boolean.*` target does nothing to that entity. `entity_service_call` finds no such entity in the switch component and logs a WARNING that the referenced entities are missing. It raises nothing, so the `except` at 6636 never fires.
  - FakeServices does not reproduce that WARNING. The failure is therefore quiet in the product, not fully silent.
  - The sibling pump driver (`coordinator.py:2706`) already uses `"homeassistant"`, which shows the codebase knows the right pattern.
- **Is the severity earned?** The failure direction is safe: the pump keeps running on its own curve. What is lost is money: savings from on/off shifting, on installs that are a minority and reach this only through one UI path. Meanwhile the plan and card show off-hours that never happen. That is a silent loss of the product's main lever for the affected users, but it does no harm to comfort or equipment, and Home Assistant logs a warning.

**Vote: weaken to medium.** The mechanism and the count (2) are verified by both harnesses and both perturbations. The high rating assumes a reach and consequence that the evidence does not support.

**Interaction with D12-s1-02:** the two are separate mechanisms. They meet at `_apply_action`: the forced `heat_pump_on=True` from the DHW boost is also unroutable on an input_boolean or climate slot.

## D12-s1-02: with no hot water configured, the DHW boost switch still puts 4 kW of DHW into the action

**Finder's harness, re-run** (`s1_phantom_boost.py`):

| arm | phantom_dhw_cells | null (DHW cells) | phantom kW | load1 |
|---|---|---|---|---|
| baseline | **8 of 8** | 0 of 8 | 4.000 (min and max) | 5.31 |
| `--fix-arm` | **0 of 8** | 0 of 8 | – | 4.93 |

With the fix, the DHW cells still show 4.00 kW, as claimed. Leave-one-out: every cell carries the same 4.000 kW, so dropping any cell leaves the others at 4.000.

**My own harness** (`v1_boost_effects.py`).

- **Metric:** no-DHW cells (zones 1 or 2, outdoor -10, 0 or +8 °C, a switch-actuated pump, a peak-priced current hour) in which a cycle after `BoostDhwSwitch.async_turn_on` differs from the same cell's no-boost cycle in any of:
  - (a) the direction of the heat-pump switch call;
  - (b) any published data key containing "dhw";
  - (c) `_commanded_power()`.
- **Differences from the finder's harness:** a different grid, a bare coordinator, and the switch entity constructed directly.

Results:
- **Baseline:** cells_changed = **6 of 6**. Each channel is 6 of 6:
  - the switch call flips from `turn_off` to `turn_on`;
  - `dhw_heating_active` flips;
  - commanded power goes from 0.00 to 4.00 kW.
- **Null control** (two no-boost cycles): 0 of 6. load1 3.33.
- **Finder's fix, applied in memory:** 0 of 6 on every channel. load1 2.89.

**Attacks on the method:**
- **Contention:** none. Every metric is a count or a kW value from the action.
- **Grid artefact:** no. All 14 no-DHW cells across both grids show an identical 4.000 kW.
- **Null control:** the finder's null arm counts a cell only when `not dhw_enabled`. On the DHW cells it therefore reads 0 by construction, not by measurement: those cells show the same 4 kW, correctly uncounted. It is really a statement about the config. My harness adds a measured null, two no-boost cycles, which reads 0.
- **Reachable in real Home Assistant?** Yes. `switch.py:46` creates `BoostDhwSwitch` unconditionally, with no DHW gate and no disabled-by-default flag, and README line 595 documents it for all users. Pressing it is a normal user action.
- **Is the severity earned?** My harness shows a consequence the finder's number does not carry. On a no-DHW install, pressing the boost switch **turns the heat pump ON during a peak hour the plan had switched off**, for 2 h, to heat a tank that does not exist. That is money spent at peak. There is also a probable effect I did not measure: `_interval_space_power` subtracts the plan's DHW allocation from metered power, so two hours of a phantom 4 kW would bias the learners on installs with a power meter.

**Vote: verify at medium.**

## Files
- `tools/audit/round8/D12/v1_switch_follow.py`
- `tools/audit/round8/D12/v1_boost_effects.py`
- The finder's `s1_actuation.py` and `s1_phantom_boost.py`, re-run unmodified.
