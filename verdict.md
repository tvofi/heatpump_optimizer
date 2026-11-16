Design review: approve 4784b5940e998aa8ef2d19436f763ff30daa46b2

Round 2. design.md read at design/R11-OUTSIDE-ROOMS-P2 4784b5940e, the tip when the review started and again before the push; the change from round 1 is `git diff be728d3e72..4784b5940e` (design.md only). Cites were checked at d4968fe08b, the head this review judges against; between the note's base 5825e1346c and d4968fe08b only coordinator.py moves among the cited production files (slab_seed wiring, at most two lines of drift after line 6664: the indoor read is coordinator.py:6648, the what-if build's margins coordinator.py:11349). Nothing was rerun: there is no code, so the solve-cost table is the designer's measurement, unverified here. Paths are under `custom_components/heatpump_optimizer/` unless they start with `tests/`.

## Round-1 points, as answered

1. Room read: a separate method beside `InputReader.read`, reading `current_temperature`, `temperature` and `hvac_action` with the unit rule of inputs.py:485-505; `_begin` (inputs.py:1006) records nothing itself, so a reader that never calls `InputHealth.record` leaves health untouched. Holds.
2. Health: rooms never enter `InputHealth`, the age tables or the range table; binary_sensor.py:100 and notifier.py:145 read only `stale_inputs`/`input_problems`. `ROOM_AIR_RANGE_C` (const.py:1876) and `QUIET_STORE_MAX_AGE_MINUTES` (const.py:297, the indoor key's limit) are cited right. Holds.
3. HVAC-mode rule stated as new, with a failing test and a mutation target. Holds.
4. Gates: `_floor_widening` (coordinator.py:6261-6269) reads `self._mode == MODE_ECONOMY` and `self._vent_cusum.tripped`; away.py:358-364 shows recovery sets no floor drop while `active` stays set, so gating on `active` covers both. Each gate has a null control. Holds.
5. All five consumers of the lifted `temp_min_bounds` are tabled; `_safety_release_steps` (optimizer.py:5001) reads space breaches only when `space_pins is not None`, and `_manual_pins` (coordinator.py:8512) returns None for an automatic channel, so the pin gate closes the release path. Holds.
6. Clip: lift_k ≤ target_k − floor_k − confidence_k, computed from the same `get_comfort_temp`/`get_temp_bounds` calls `_build_comfort_bounds` makes (optimizer.py:4525-4551); the `temp_max_bounds − 0.5` clamp (optimizer.py:4576-4578) is left as is, so invariant (i) holds. Holds.
7. Ramp anchored on the present margin, a deadband hold, the what-if reading the held lift, two-zone gated off, and table rows starting 0.4 K under the lifted floor single- and two-zone. Holds.
8. 3b re-cut out with its constraints stated (optimizer.py:331, :4750; both composition sites). Holds.
9. `tests/golden/config_flow.json` re-recorded without a claim, `tests/entities.py` page pin and `collect()` fixture named. Holds.

Sibling designs in flight: every open `design/*` ref was grepped for `min_temp_margins`, `power_caps_extra`, `_build_comfort_bounds`, `_confidence_margins`, `_floor_widening`, `SolveLimits`, `InputReader` and the room list; none claims them. design/R11-OUTSIDE-HONEST-METERED-FLOOR ef9b12e7dd shares `store.DOMAINS` and sensor.py (different entities); R10-START-COUNTER-EDGES 18655c84b6 cites sensor.py:2776 only. Shared files, not a shared seam.

## Decisions routed (no revise point)

- decision: owner. The holiday profile lowers the floor through `get_temp_bounds` (slot_drivers.py:42 `away_floor_drops` measures that drop), and the note keeps the lift there and at night, clipped to the band. Room thermostats keep their own targets through a holiday, so the raw lift is large for its whole length and the clip holds the house at the holiday target instead of letting it float to the holiday floor. Away is gated off for the reason stated in the note's away rows; whether the holiday profile yields the same way (one more gate, same signal `away_floor_drops` reads) or keeps the lift as designed is a product choice. Recommended: yield, as away does.

## Notes for the fixer (carries)

- The P2 failing test expects 0.5 at every day step with the house at 19.6 over a 19.5 floor, but the note's own ramp sets step 0 to the house's margin over the floor (0.1) and reaches 0.5 only after 1.6 h at 0.25 K/h; the expected array is min(band, margin + rate × lead), or the fixture starts the house at or above 20.0 for the flat case. Carry: R11-OUTSIDE-ROOMS-P2 (item v2a)
- The what-if runs on `quiet_windows.overridden_config` (coordinator.py:11307), so its per-step clip must be computed from the what-if's own configuration with the baseline's held scalar and ramp anchor, not reuse the baseline's clipped array; pin both halves. Carry: R11-OUTSIDE-ROOMS-P2 (item v2b)
- "Raw lift" uses "the live comfort target" for the house shortfall while the clip is per-step; name which step's target (step 0's `get_comfort_temp` of the solve's configuration) so a solve that starts at night does not mix a day target into the scalar. Carry: R11-OUTSIDE-ROOMS-P2 (item v2c)
- The two-zone cite optimizer.py:2421 is `sensor_trajectory`, not where `state.room_temperature` is defined as the upper floor; re-anchor to the state's field or the reader in `_update_current_state`. Carry: R11-OUTSIDE-ROOMS-P2 (item v2d)
- Note item s1 says `_begin` "may record into health on its early exits": at d4968fe08b it does not (inputs.py:1006-1056 only sets `reading.problem` and returns); the control still stands as written. Carry: dismissed: premise checked false (item v2e)

Seat tokens: the harness reports none for the main loop; no scouts were used.
