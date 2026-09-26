# D8, verifier V3 (reach and class), round 9, box G2-V3

**Box:** G2-V3, 4-CPU container, CPython 3.14.0rc2. **Tree:** evidence 6f51db2c on baseline 1936d5ca.

**Real Home Assistant:** homeassistant 2026.2.3 in its own venv. It would not import `homeassistant.helpers.entity` on 3.14.0rc2 because the bundled mashumaro reads `typing.ByteString`, which 3.14 removed. A harness-local shim (`verify-v3/hashim/sitecustomize.py`) re-adds that name and appends the gate venv's site-packages for numpy and scipy; the probe asserts `homeassistant` is not loaded from the hastub. The frontend wheel HA 2026.2.3 pins (`home-assistant-frontend==20260128.6`) was read (in scratch) for how its device page groups and sorts entities.

**Harnesses** (under `tools/audit/round9/D8/verify-v3/`):
- `real_ha_probe.py`: a real `HomeAssistant`, the real climate and switch `EntityComponent`, real service dispatch, the real state machine.
- `own_stub.py`: own metrics against the stub.
- `step1_reruns.txt`: every RESULT line from re-runs, perturbations and own harnesses.

**Load:** every step-1 count reproduced exactly, load1 0.38–3.38, thread_factor 1.000. `real_ha_probe` reports thread_factor 1.013–1.062 from real HA's executor threads; every number it gives is a count or a state, not a timing.

---

### D8-s1-01: Current Electricity Price publishes an earlier quarter's price at 15-minute resolution
- **Step 1:** `price15.py` wrong_quarters=95, worst error 0.30. `--hourly` 0, `--fix` 0, `--cycle` 95 with sensor-minus-plan 0.08. load1 0.38–0.51, thread_factor 1.000. Matches.
- **Step 2:** real `homeassistant.util.dt` in Europe/Stockholm; price rows built by production `prices_from_entity_state` from a 96-row Nord Pool `raw_today` (keeps all 96 rows, no resampling). `s1_01_wrong_quarters=95` of 96; `--perturb` (entry covers [start, next start)) 0.
- **Attacks:** contention none (count); gate mode n/a; grid: whole day counted; null: hourly arm 0. Reach: **real** — `pull_prices` asks Tibber with `TIBBER_PRICE_QUERY_QUARTER` first and the entity source keeps 15-minute rows, so every Tibber install and every Nord Pool install since the 15-minute market reaches it; no stub symbol involved. Severity: **high earned** — `_get_current_price` feeds the published price, the settlement's pending `price` (ledger books spot and fee), the comfort learner and the fixed-mode action price.
- **Seam rule:** 2 hits. Line 6333 is the defect; line 6034 is `_known_prices_for`'s last-entry fallback, correct. A package-wide grep finds no other covering-now search. **All.**
- **Class:** P2 confirmed ("which entry covers now" decided by `[start, next start)` in the plan path and by a fixed 1 h window here).
- **Vote: verify, high.**

### D8-s1-02: DHW Heating Schedule counts 15-minute steps as "heating periods"
- **Step 1:** `s1/matrix.py` (full, 19.5 min) dhw_periods_vs_slots=92; `--only +dhw` 12, `--perturb-dhw-runs` 0. load1 0.73–1.87. Matches.
- **Step 2:** after two real cycles, 2 of 2 DHW cells differ: "9 heating periods" against slot_count=5, worst ratio 1.8.
- **Attacks:** not a grid artefact (leave-one-out min 2). Reach: real (pure payload logic into the real state machine). `tests/entities.py` #284 pins "two consecutive steps = 2 heating periods", so the suite agrees with the mislabel. Severity: **low earned** (label only, nothing actuated).
- **Seam rule:** **partial.** 2 hits (the sensor's `> 0.1` and `_plan_slots`' 0.05). The same "is DHW heating" fact is decided at `optimizer.py:6231/6281/6287/7105` (`> 0.1`) and `coordinator.py:3389` `active_now` (`> 0.05`), so `dhw_heating_active` and `active_now` also diverge.
- **Class:** P2 confirmed.
- **Aside:** an unrelated grep landed on an older register row describing the same "N heating periods counting quarter-hour steps" text. Its verdict played no part in this vote; the judge may want to check for a duplicate.
- **Vote: verify, low.**

### D8-s1-03: Recommended Power publishes a sub-threshold draw while Heat Pump Action reads "off"
- **Step 1:** `minpower.py` 4 at min_power 1.0 (0 in other arms), worst 0.41 kW; `--perturb` 0. Matrix power_while_off=2. Matches.
- **Step 2:** different price shape, default min power 1.0, 5 topologies × 96 steps: 23 of 480 steps have `heat_pump_on` False with `commanded_power_kw` > 0.05 kW (worst 0.46). At the same 23 steps production `coordinator._commanded_power()` is also > 0.05.
- **Attacks:** reach real (default min power 1.0 puts the on-threshold at 0.5; pure logic). Severity: **low earned for the entities.** Internal consumers — settlement `_pending_prediction["power"]`, the COP fold, the frequency command, external-heat detection — are a sibling seam; their input was measured, not their downstream effect.
- **Seam rule:** **partial.** Greps `commanded_power_kw(` (4 entity sites); misses `_commanded_power()` and `_commanded_split()`, about 12 call sites in `coordinator.py` summing the same ungated power.
- **Class:** P2 confirmed ("is the pump on" decided by `heat_pump_on` in one place, by power > 0 in another).
- **Vote: verify, low.**

### D8-s2-01: Climate entity permanently unavailable without an indoor thermometer
- **Step 1:** climate_unavailable_with_payload=5, climate_attrs_hidden=112; `--perturb-available` 0 and 0. Matches.
- **Step 2 (real HA):** with no reading, state `unavailable` with 6 attributes; 0 of 3 real service calls reach the entity (`set_hvac_mode`, `set_temperature`, `turn_off`) because HA 2026.2.3's `helpers/service.py` skips `not entity.available` silently, raising nothing. Perturbed (reading_ok True): state `auto`, 34 attributes, 3 of 3 calls reach.
- **Attacks:** reach **real** (README: indoor thermometers optional). Severity: control lost only in part — the Optimizer Active switch, `heatpump_optimizer.set_mode` and the options flow still work, and nothing is actuated wrongly. Lost: the device's main entity, the thermostat card, and any climate-targeted automation (a silent no-op). It is also a pinned A3(e) decision, so it needs the owner. **Medium.**
- **Seam rule:** 1 hit; `datetime.py`, the only other control platform, has no `available` override. **All.**
- **Class:** new — a whole entity's availability gated on an optional input's reading where a per-field None already meets the aim.
- **Vote: weaken, medium.**

### D8-s2-02: Climate hvac_action publishes off while a boost runs the pump in mode off
- **Step 1:** 14 arms, 0 in the auto null arm; `--perturb-hvac-action` 0. Matches.
- **Step 2 (real HA):** payload mode off with a boost action at 5 kW: state `off`, hvac_action `off`. Action-first read emulated: `heating`.
- **Attacks:** reach real (`boost.apply` runs in every mode; README: Boost does not switch the optimizer mode). HA's hvac_action means what the device is doing now, so the misreport is genuine and lasts up to the 2 h boost; Heat Pump Action reports `boost`/`hot_water` for the same step via `overlay`. Severity: no wrong actuation; heating-time history and hvac_action automations under-report. **Medium.**
- **Seam rule:** climate.py only; no other operating-state property derived from the mode label package-wide. **All.**
- **Class:** corrected "new" → **P2** ("is the pump running" read from the action by Heat Pump Action, from the mode label by the climate).
- **Vote: weaken, medium.**

### D8-s2-03: Mode actions publish a state mixing the live mode with the stale payload mode
- **Step 1:** mode_split_after_action=2; `--perturb-live-mode` 0. Matches.
- **Step 2 (real HA):** 4 of 4 mode transitions dispatched as real services leave a split state (twice the finder's 2). The reverse direction also splits once the background refresh really runs: turning on shows `auto` with hvac_action `off`, the switch on with mode `off`. Windows: 1.0 s (fake refresh time) for the first transition, then 10.9 s for each later one (HA's 10 s refresh-debouncer cooldown).
- **Attacks:**
  - **The claimed "30 to 70 s" does not hold for the demonstrated off direction**: the cycle's MODE_OFF branch runs no solve, so the window is fetch time plus at most 10 s cooldown. The auto direction was not bounded (the stub run ran no solve: 8 ms CPU vs 5 ms for off).
  - **The climate half matches HA semantics**: the pump keeps its old state until the refresh actuates and hvac_action reports exactly that — 0 of 2 climate writes misreport the actuated state.
  - The proposed fix (hvac_action reads the live `coordinator.mode`) would publish OFF while the pump still runs — D8-s2-02's misreport — so the two fixes conflict.
  - Only the switch's `mode` attribute is a genuinely stale label, for seconds; cosmetic.
- **Seam rule:** 2 hits; the only other payload-mode reader, the Optimization Mode sensor, has a single source. **All.**
- **Class:** corrected "new" → **P2**.
- **Vote: weaken, low.**

### D8-s3-01: Accuracy and energy-meter families split in the name sort
- **Step 1:** families_split_unexplained 2 (en), 2 (sv), 1 (entity_id); `--perturb` 1 and 1. Matches.
- **Step 2:** the real frontend 20260128.6 device page buckets entities first (assist/event/notify by domain; else `entity_category`; else Sensors for sensor-like domains; else Controls), then name-sorts within a bucket.
  - The **energy meters** split into 3 runs inside the Sensors card, en and sv: real.
  - The **accuracy family** is split across buckets (Diagnose Last Interval button, category None, in Controls; Prediction Accuracy, DIAGNOSTIC, in Diagnostic). No name makes them adjacent there, and the finder's rename perturbation does not change the device page.
  - `s3_01_device_page_split=2`, `s3_01_cross_bucket=2`. The default sort of the flat Settings → Entities table was not verified.
- **Severity:** low hygiene; half the demonstrated scope is not reachable on the device page.
- **Seam rule:** **partial** — 8 hand-listed families, and a flat six-platform ordering rather than the device page's category buckets.
- **Class:** new, accepted.
- **Vote: weaken, low (scope reduced to the energy meters).**

### D8-s3-02: Swedish Sensor-Gap Advisor name
- **Step 1:** concept_mismatch=1 over 74 names; `--perturb` 0. Matches.
- **Step 2:** an independent currency-word asymmetry scan over every en/sv entity name finds 1, the same key: en "Sensor-Gap Advisor", sv "Sensorlucka i valutan".
- **Reach:** real — HA resolves `component.heatpump_optimizer.entity.sensor.sensor_gap_advisor.name` from `translations/sv.json` (`Entity._name_translation_key`).
- **Severity:** low. **Seam rule:** **partial** (hand-built concept map; the currency scan agrees).
- **Class:** I5 confirmed (text stale against the rename), though I5 is instrument-kind and this string is user-facing.
- **Vote: verify, low.**

### D8-s3-03: Upper Floor Temperature duplicates Indoor Temperature and is enabled by default
- **Step 1:** duplicate_enabled_pairs=1; `--perturb` 0 while duplicate_pairs_any_default stays 1. Matches.
- **Step 2:** equal values and both enabled in 5 of 5 topologies; `coordinator.py:5343/5345` is the only writer of both fields.
- **Real HA:** no class in the integration's MRO overrides the registry default, so HA 2026.2.3's `entity_registry_enabled_default` returns True. `entity_platform` sets `disabled_by=INTEGRATION` only on first registration, so a new-install-only default is achievable without touching existing registries.
- **Severity:** low; the docstring records a deliberate keep, and the proposed fix does not conflict with its stated concerns.
- **Seam rule:** **partial** (full pairwise scan, numeric same-unit sensors only).
- **Class:** new, accepted.
- **Vote: verify, low.**

---

**Counts:** verify 5, weaken 4, refute 0, unresolved 0.

**Not measured:** the flat entities-table sort (D8-s3-01) and the auto-direction solve window (D8-s2-03).
