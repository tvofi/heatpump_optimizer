# D6 round 9 — verifier V1 (reproduce)

Box G4-V1. Unit D6: D6-s1-01..04 and D6-s2-01..05.

## Environment
- Worktree: `handoff/audit-r9-evidence` at 6f51db2 (baseline 1936d5ca plus the round-9 evidence).
- `PYTHONPATH=tests/hastub`. `/home/claude/venv/bin/python` (CPython 3.14.0rc2, `tests/requirements-ci.txt` pins) stands in for the headers' venv314.
- `claims.py` was run with `--no-net`.
- Load: load1 0.41–1.91 during the finder re-runs and 3.04 during the independent run. thread_factor 1.000–1.002.
- Every metric is a count, so contention does not affect it.

Harnesses and logs are under `tools/audit/round9/D6/verify-v1/`:
- `independent.py` holds the independent measurements. Run it with `PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D6/verify-v1/independent.py`; its output is in `independent.log`.
- Finder-harness logs, one per arm:
  - `s1_claims{,action_states,orientation,dhw_config,clamp_expiry}.log`
  - `flow_{none,perturb,perturbcount}.log`
  - `beh_{none,curve}.log`
  - `hiw_{none,starts}.log`
  - `svc_{none,perturb}.log`

## D6-s1: `claims.py --no-net`, one run per arm

| arm | action_states_undocumented | option_page_misplaced | no_dhw_disabled_undocumented | manual_pin_hours_beyond_20 |
|---|---|---|---|---|
| none | 2 | 3 | 6 | 4.0 |
| action_states | **0** | 3 | 6 | 4.0 |
| orientation | 2 | **2** | 6 | 4.0 |
| dhw_config | 2 | 3 | **0** | 4.0 |
| clamp_expiry | 2 | 3 | 6 | **0.0** |

The baseline row equals the finder's numbers exactly. Each perturbation moves its own metric, and only that one, in the stated direction.

### D6-s1-01: Heat Pump Action states — verify, low
- **Re-run:** 2. **Perturbation:** 0.
- **Independent check:** `const.HEAT_PUMP_ACTION_STATES` holds `idle`, produced by `optimizer._idle_action` (optimizer.py:6972), and `system_identification`, produced by `coordinator._run_system_identification` (coordinator.py:10538). README.md:461 names neither state, and neither word appears anywhere in README.
- **Reachability:** both states occur in real Home Assistant. `system_identification` follows the sysid button; `idle` follows an empty plan or a moment before the horizon starts.

### D6-s1-02: options page placement — verify, low
- **Re-run:** 3. **Perturbation:** 2. **Leave-one-out:** 2.
- **Independent check:** config_flow.py:1662-1665 puts inter-zone transfer, radiator fraction and orientation factor on `thermal_model_zones`. README.md:392-395 names other pages for them.
- **Attack:** the count is conservative. The per-floor masses and losses (lines 1658-1661) are also on the zones page, so a wider reading of README's "masses, losses" raises it.

### D6-s1-03: disabled entities on a no-hot-water install — verify, low
- **Re-run:** 6. **Null control (tank configured):** 0. **Leave-one-out:** 5.
- **Independent check:** six `DHWEntityMixin` sensor classes (sensor.py:1168, 1211, 1595, 1789, 1836, 2279) have README rows 477, 478, 490, 494, 518 and 539. None of those rows says the entity is disabled, and README.md:438 says "Nineteen".
- **Attack:** "ordinary install" could be read as an install with hot water. README documents the Finish-setup-now path without hot water, so the gap stands on a documented path.

### D6-s1-04: apply_manual_plan "up to 20 hours" — verify, low
- **Re-run:** 4.0 h. **Perturbation (clamp):** 0.0.
- **Independent check** (`build_override` plus `channel_pins`, 96 steps):

  | expires_at | hours pinned |
  |---|---|
  | default (null control) | 20.0 |
  | +24 h | 24.0 |
  | +48 h | 24.0 |
  | +48 h clamped | 20.0 |

- **Attack:** no downstream clamp exists. services.py:867-884 accepts any parsed expiry, and coordinator.py:7457 uses the pins directly. The overrun is bounded only by the 24 h horizon.

## D6-s2

### D6-s2-01: "All 74 entities" — verify, low
- **Re-run (`flow_census.py`):** total 75, delta 1. By platform: sensor 59, binary_sensor 6, button 4, climate 1, switch 4, datetime 1.
- **Perturbation (`--perturb-count`):** delta 0 and total 74. architecture.md becomes WRONG twice, as the header predicts.

### D6-s2-02: the weather page does not create the entry — verify, low
- **Re-run:** `weather_submit_creates_entry` 0, `wizard_steps` 11. **Perturbation:** 1 and 10.
- **Driven path:** user → user_sensors → menu:finish_setup → temperature → menu:building → building_describe → building_extras → dhw → weather_sensitivity → setup_overview → create_entry.
- **Independent check:** config_flow.py:2883 returns `async_step_setup_overview`, and the entry is created at :2507. The flowchart at configuration.md:24-38 has neither the menu nor the overview step.
- **Reachability:** this is the real flow class. Forms and menus behave the same in real Home Assistant.

### D6-s2-03: curve bias "at most 0.5 K per week" — verify, low
- **Re-run:** 0.600 K. **Null control (`--perturb-curve`, cap 0.3):** 0.457.
- **Independent check:** 9 cells (margins 0.5, 1 and 3 × 3 start dates) all give 0.600. Leave-one-out: 0.600.
- **Mechanism:** curve_learning.py:106-121 checks the cap against the previous step only. Steps of 0.2 K every 3 days put 0.6 K inside one 7-day window.
- **Attack:** as a long-run average (0.467 K/week) the claim holds. But the doc and the code's own comment both state a cap per 7 days, and that cap is broken.
- **Class:** for the judge; I lean bug.

### D6-s2-04: "two starting points" — verify, low
- **Re-run:** 4 candidates, 8 minimize calls. **Perturbation (`--perturb-starts`):** 2 and 4.
- **Independent check:** a spy on 4 cells found 4 candidates single-zone and 5 two-zone, in both winter and shoulder. Leave-one-out: minimum 4, maximum 5.
- **Not re-measured:** the 2.2 % and 0.2 % figures.

### D6-s2-05: simulate_plan field list omits the wood fields — verify, low
- **Re-run:** 5 fields: wood_furnace_efficiency, wood_packing, wood_price_sek_m3, wood_slots, wood_type (16 schema keys, 11 listed).
- **Method defect:** the recorded `--perturb` edits `set_thermal_parameters` and `set_mode`. It moves `services_claims_false` from 1 to 5 but leaves this finding's own metric at 5. Read strictly, the recorded perturbation voids the finding.
- **Replacement perturbation (executed):** dropping the `wood_*` keys takes the metric to 0.
- **For the judge:** the claim is correct. Adopt the replacement perturbation.

## Not done
- No mutation work (tvofi's no-heavy-D3 rule).
- No link checks (`--no-net`).
- The 2.2 % and 0.2 % solve figures in how-it-works.md were not re-measured.
