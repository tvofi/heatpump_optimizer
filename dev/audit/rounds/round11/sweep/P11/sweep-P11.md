# Round 11 class sweep: P11 (a hand-written double is the only oracle)

Class P11 (`dev/audit/config/bugclasses.json`): the only oracle for an external
counterpart is a test double the implementer wrote from what the code needed, so the
tests agree with a wrong implementation. Ledger status: `barriered`. The barrier is
`tests/ha_contract.py` plus the floor-name arm in `tests/entities.py`. Neither has a
contract for `hass.services.async_call`: the only service-related entry,
`ServiceCall`, is `SIMPLIFIED`.

The judged finding is **D16-s1-05** (verified, low). `pump_arbiter._write` gates on
`state is None` and never on `unavailable`, and it books the mode write in
`held.written` after the call. Home Assistant's entity service call skips an entity
that is not available, without raising. The double, `tests/harness.py:FakeServices.async_call`,
records and dispatches every call and never reads the target's state, so the suite
agrees with the wrong booking.

All commands below run from the register worktree (`origin/handoff/audit-r11-register`,
28b864af).

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep-P11/p11_write_records.py`

- **Seam.** A package function that performs a write and, after it in the same
  function, records the write as made. That record is an assignment to an attribute or
  subscript, or a `note_command`/`append`/`_record_write`/`_report_write` call. A write
  is `services.async_call`, or a package function calling it directly or through up to
  two wrappers (`write_setpoint → write_setpoint_c → _valve_write_problem`).
- **Flag.** The function's code, with comments and docstring excluded, never tests the
  target's availability: no `unavailable`, `STATE_UNAVAILABLE` or `.available`, and no
  `number_reading(...)` with an `is None` test before the write.

Output: `seams=17`, `flagged=16` (`D14/sweep-P11/p11_write_records.out`). As a
cross-check, the write universe that `tools/audit/enumerate.py d16-writes` prints has 8
service-call sites (`d16_writes.out`). Six of them are inside these seams or their
callees. The other two are `heat_curve.publish_ecl110_topics`'s `mqtt.publish` calls,
which are not seams: they have no entity target for Home Assistant to skip, and their
function books nothing after the publish.

| control | result |
|---|---|
| positive (re-finds D16-s1-05) | `pump_arbiter.py::_write write@1608 record@1616 FLAG` |
| null (`--null`: a fixture that returns on an unavailable state before writing) | `flagged=0` |
| perturbation (`--perturb`: that fixture's one guard line reduced to `state is None`, the finding's shape) | `flagged=1` |

The flag over-approximates: it cannot see a read-back after the call or a pre-check
inside a helper. The dispositions below settle each seam.

Probes: `PYTHONPATH=tests/hastub:. python3 dev/audit/rounds/round11/D14/sweep-P11/p11_probes.py`.
Each arm drives the real writer through a services double that skips an unavailable
target, as Home Assistant does. The target is unavailable on cycle 1 and available on
cycle 2, and the arm counts a command booked but never delivered. The null is
`--double fake`, which lands every call as FakeServices does: 0. The perturbation is
`--perturb`, where the writer returns before the call on an unavailable target: 0.
Output is in `p11_probes.out`.

The skip itself is taken from D16-s1-05's own emulation (`cells.py`, which the verifier
and judge reproduced) and from the package's own statement in `disinfection.py`'s class
docstring. This sweep did not re-read upstream Home Assistant source.

## Dispositions (all 17 seams)

**Instance**
| seam | disposition |
|---|---|
| `pump_arbiter._write` | the judged site (D16-s1-05): `cells.py --no-gates` prints `unavailable_recorded=5` rigs at the register head |
| `coordinator._async_set_pump` | **beyond the finding.** `homeassistant.turn_on/off` to an unavailable pump is skipped, yet `_pump_commanded[entity] = on` is booked. Next cycle the dedup (`previous == on`) returns, so the pump is never commanded once it is back: `set_pump_lost_command=1`, null 0, perturbation 0. The code's comment says the opposite ("a command that failed (entity briefly unavailable) must be retried next tick"). That comment's model of HA, an unavailable entity raising, is the double's model |
| `coordinator._command_frequency` | **beyond the finding.** `number.set_value` to an unavailable compressor-frequency entity is skipped, yet `_freq_last_write` and `_freq_watchdog.note_command(target)` are booked. The epsilon dedup against `watchdog.commanded` then refuses the resend while the target holds: `frequency_lost_command=1`, null 0, perturbation 0. The watchdog's report divergence can trip later; it reads the event as a pump not following, not as a write never made |
| `coordinator._command_valve_target` | **beyond the finding.** `write_setpoint_c` to an unavailable valve-target entity is skipped, yet `_valve_commanded_target` is booked. The `MIXING_VALVE_WRITE_EPSILON` dedup holds until the target moves: `valve_lost_command=1`, null 0, perturbation 0 |

**Guarded**
| seam | guard |
|---|---|
| `disinfection.DisinfectionSwitch.turn_on`, `.release`, `.release_blind` | read-back: `_write` refuses with no call when `_flag_now` is None, and a write counts only when the target reads back the commanded state after it (`disinfection.py` around line 232; class docstring "Landed means read back") |
| `legionella.LegionellaGuard._drive_switch`, `.async_track_cycle` | they write through `DisinfectionSwitch`, with the same read-back. `memo` is set only on a confirmed write |
| `heat_curve.write_displace` | `number_reading(...)` is None for a non-numeric state, so the function returns before any call. `_decide` also compares the read-back value with the last write |
| `early_cutoff.on_room_event` | pre-check: `_cycle_guard` refuses unless the supply switch reads `"on"` (early_cutoff.py around line 268), so an unavailable switch is never cut or booked |

`heat_curve.write_persistent` and `_write_persistent_target` are not seams of the rule,
because the record (`_record_write`, line 566) comes before the send. They are guarded
anyway: `reading is None` returns before either (lines 504–505).

**Not applicable**
| seam | reason |
|---|---|
| `coordinator._fetch_weather_forecast` | a read service (`weather.get_forecasts`, `return_response=True`). A skipped or empty response takes the stale branch; nothing is booked as written |
| `coordinator._async_update_data`, `coordinator._update_current_state` | no service write of their own. They matched through a transitive name, and the record is cycle bookkeeping (`_refresh_task`, `_pump_signals`) |
| `early_cutoff.arm`, `early_cutoff.detach` | the record after `release(held)` is the listener subscription or wiring, not a write booking |
| `config_flow.HeatPumpOptimizerOptionsFlow.async_step_quick_setup` | an options-form step; the matched writer is a flow-step name, and the record is a form dict |

## Count and barrier

There are 4 instance seams: the judged site and **3 beyond it**, all in the coordinator.
They share one root: a write is booked when `services.async_call` returns, and the only
oracle (`FakeServices`) never skips an unavailable target. The class's existing barrier
(`ha_contract.py`) does not reach it, so `barriered` is `false` for this shape.

Proposed barrier, in two parts:

1. Model the skip in `tests/harness.py:FakeServices.async_call`: a call whose
   `entity_id` reads `unavailable` dispatches nothing. Give it an `expect="real"`
   contract in `tests/ha_contract.py` that cites `helpers/service.py`'s
   entity-service skip and is re-asked in the nightly-ha image.
2. Gate on `p11_write_records.py` with an allow-list of the guarded seams above. A new
   write-then-book seam then needs a read-back or an availability pre-check, or an
   entry in the allow-list.

The cost is an AST pass in the gate plus whatever suite cases start failing once the
double is faithful. Those failures are the instances above, by construction.
