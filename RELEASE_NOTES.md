# Heat Pump Cost Optimizer — Release Notes

## v2.3.0

### Summary
This release reworks domestic hot water (DHW) optimization. Hot water is now
required only during time frames you configure, and it is produced with a
cheapest-first schedule instead of a target temperature the optimizer tried to
track regardless of price.

### Fixed
- **DHW no longer heats to high setpoints during price peaks.** The objective
  previously contained a "comfort" term that penalised any deviation from a
  ramped DHW target temperature. Its weight was orders of magnitude larger than
  the electricity cost term, so the solver effectively ignored price and heated
  the tank to setpoint whenever it drifted — including in the most expensive
  hours and while space heating was idle. DHW is now penalised only for
  *violating an availability requirement*, never rewarded for being hot, which
  leaves electricity cost as the only thing deciding when the pump runs.
- **DHW plans are now physically realizable.** The gradient solver used to smear
  DHW across many steps at 0.1–0.5 kW, below the level at which the heat pump is
  considered to be running. DHW is now scheduled as discrete on/off blocks.
- **The 45 °C floor no longer applies around the clock.** It applies inside the
  demand time frames; outside them the tank may cool to the idle minimum.

### Added
- **Hot water demand time frames.** Configure when hot water must be available,
  e.g. `06:00-08:30, 17:00-22:00`. Frames may wrap past midnight and are
  editable from both the setup dialog and the options dialog.
  - Inside a frame the tank is guaranteed at or above the DHW minimum
    temperature.
  - At the start of a frame the tank is pre-heated only as far as that frame's
    expected draw requires, capped at the DHW setpoint — small consumers are no
    longer heated to full setpoint for no reason.
  - Outside the frames there is no availability requirement.
  - Leave the field empty to derive the frames from the learned usage profile,
    or switch the schedule off to require hot water around the clock.
- **Anti-legionella cycle**, enabled by default: the tank is heated to 60 °C
  every 7 days, scheduled at the cheapest hour before the deadline. The timer
  resets whenever the tank is observed at the disinfection temperature for any
  reason, so manual boosts and immersion heaters count. Temperature and interval
  are configurable, and the cycle can be turned off.
- **Idle minimum temperature** (default 20 °C) — the floor that applies outside
  the demand time frames.
- New DHW sensor attributes: `dhw_windows`, `dhw_in_demand_window`,
  `dhw_next_window_in_hours`, `dhw_required_temperature`,
  `dhw_idle_min_temperature`, `dhw_legionella_due_in_hours` and
  `dhw_planned_heating_hours`.

### Changed
- **Two-stage solve.** DHW is scheduled by a cheapest-first planner, then space
  heating is optimized around the fixed DHW blocks with the pump's remaining
  capacity as a hard per-step bound. This replaces the joint solve and its soft
  capacity penalty, so the capacity limit can no longer be violated.
- Slot ranking uses an *effective* price that includes the standby heat lost
  while water waits in the tank, so pre-heating many hours ahead is only chosen
  when it is genuinely cheaper.
- The tank is never planned above `min(70 °C, max(setpoint, legionella temp))`.
- The learned hourly draw pattern is masked by the configured time frames while
  preserving the total daily volume.
- Typical solve time with DHW enabled dropped from roughly 6 s to under 1 s, and
  the solver no longer hits its iteration limit.

### Configuration options
| Option | Default |
|---|---|
| `dhw_schedule_enabled` | `true` |
| `dhw_windows` | `06:00-08:30, 17:00-22:00` |
| `dhw_idle_min_temperature` | `20` °C |
| `dhw_legionella_enabled` | `true` |
| `dhw_legionella_temperature` | `60` °C |
| `dhw_legionella_interval_days` | `7` |

### Upgrade notes
Existing installations pick up the default time frames on upgrade. If your
household draws hot water at other times, set `dhw_windows` in the integration
options. To keep the previous always-hot behaviour, turn off *Only guarantee hot
water during set time frames*.

## v2.2.0
**Release date:** 2026-04-27

### Summary
This minor release introduces a new, preferred ECL110 MQTT direct-write control path while keeping full backward compatibility with existing legacy JSON command workflows.

### Highlights
- **New ECL110 direct-write MQTT interface (preferred):**
  - Commands are now published as plain numeric payloads to a dedicated `/set` topic for cleaner, lower-overhead control.
  - Default direct-write topic: `ecl110/flow_temp_control/displace/set`.
- **Backward compatibility preserved:**
  - Legacy JSON command publishing remains supported on `ecl110/command`.
  - Existing ECL110 installations using the previous JSON interface continue to work without mandatory migration.
- **Broader state payload compatibility:**
  - State handling now supports both legacy JSON/dictionary payloads and scalar numeric payloads from hierarchical topic structures.
- **Improved configuration UX:**
  - Added a new configurable option: `ecl110_displace_set_topic`.
  - Existing `ecl110_command_topic` labeling has been clarified as the **legacy JSON path**.
  - Updated UI strings/translations for clearer topic purpose in both setup and options flows.

### Configuration options
The following MQTT topic settings are now available for ECL110 control:
- `ecl110_displace_set_topic` *(new, preferred direct-write path)*
  - Default: `ecl110/flow_temp_control/displace/set`
- `ecl110_command_topic` *(legacy JSON path, optional for compatibility)*
  - Default: `ecl110/command`
- `ecl110_state_topic` *(state feedback topic)*
  - Default: `ecl110/flow_temp_control/displace`

### User impact
- Recommended for users integrating with ECL110 hierarchical MQTT topics and direct numeric control.
- Existing users can safely upgrade without immediate topic migration.
- Integrators can run both paths in parallel during transition if needed.

### Notes
- This is a backward-compatible minor release.
- No required database/config migration for existing installations.

## v2.1.0
**Release date:** 2026-04-23

### Summary
This release improves Domestic Hot Water (DHW) optimization to prioritize cost savings while maintaining safe hot water availability.

### Highlights
- **Configured DHW minimum temperature is now actively enforced as the true floor** in optimization logic.
- **Predictive DHW pre-heating** now uses forecasted usage windows and estimated lead-time so the tank can coast near minimum between peaks.
- **Price-aware DHW control** reduces heating in expensive periods when no near-term hot water usage is predicted.
- **Learning usage patterns over time** from observed DHW temperature drops, persisted across restarts.
- **Post-install editability improvements** in the options flow for comfort/day-night schedule and DHW parameters.
- **Branding update**: added integration icon (`icon.png`) for HACS/repository branding.

## v2.0.1
**Release date:** 2026-04-21

### Summary
This patch release fixes a critical control logic issue that could prevent Domestic Hot Water (DHW) reheating when space heating demand was low or zero.

### Fixed bug
- **Critical ON/OFF control fix:**
  - The heat pump ON decision now correctly considers **both**:
    - space heating demand, and
    - DHW demand.
  - Previously, ON/OFF logic only evaluated space heating demand, which could keep the heat pump OFF even when DHW needed heating.

### Improvements and changes
- Updated ON/OFF schedule generation to use combined demand logic (`space OR dhw`) so the heat pump can activate for DHW-only demand periods.
- Added enhanced debug logging for optimizer decision-making, including:
  - per-step space heating power,
  - per-step DHW power,
  - threshold comparisons,
  - explicit decision reason tags (for example: `space_only`, `dhw_only`, `space_and_dhw`).
- Added clearer first-step decision summary logging to simplify troubleshooting during live operation.

### User impact and benefits
- Prevents missed DHW reheating cycles when there is no immediate space heating demand.
- Improves comfort and reliability by ensuring DHW demand can independently trigger heat pump operation.
- Makes behavior easier to diagnose with richer decision logs.
- Reduces risk of confusion where optimization output indicated DHW demand but physical heat pump stayed OFF.

### Upgrade instructions (HACS)
1. Open **HACS → Integrations**.
2. Find **Heat Pump Cost Optimizer**.
3. Click **Update** and install **v2.0.1**.
4. Restart Home Assistant (recommended after integration updates).
5. Verify operation:
   - Confirm integration version shows **2.0.1**.
   - Check logs at debug level if needed to validate combined ON/OFF decisions for space heating and DHW.

### Notes
- This is a backward-compatible patch release focused on control correctness and observability.
- No configuration migration is required.
