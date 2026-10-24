# D8 verification report (sole verifier, round 8)

Tree: `/home/claude/audit-r8/seats/D8-v1`
Baseline SHA: `cdf82daabcfe3777d98b31489f36df5555ec9d82`
Evidence copied in from `D8-s1` and `D8-s2` (`cp -rn .../tools/audit/round8/D8/. tools/audit/round8/D8/`); no path rewriting was needed, no harness hard-coded another seat's absolute tree path.

Per the note in the task ("This round's panel has ONE verifier... you carry both halves of verifier.md"): for each finding I re-ran the finder's harness verbatim, wrote and ran my own harness under an independently-written metric definition, and applied the method attacks from `verifier.md` in order.

---

## D8-s1-01 — climate/switch/binary_sensor/datetime leak NaN/Inf; only sensor.py scrubs

**Re-run of finder's harness** (`s1_finite_boundary.py`, verbatim):
```
RESULT climate_class=HeatPumpOptimizerClimate name
RESULT null_control_ok=1 bool  climate=0.73 sensor=0.73
RESULT climate_leaks_nonfinite_nan=1 bool value=nan
RESULT sensor_scrubs_same_key_nan=1 bool value=None
RESULT climate_leaks_nonfinite_inf=1 bool value=inf
RESULT sensor_scrubs_same_key_inf=1 bool value=None
RESULT climate_finite_call_count=0 count
RESULT switch_finite_call_count=0 count
RESULT binary_sensor_finite_call_count=0 count
RESULT datetime_finite_call_count=0 count
RESULT sensor_finite_call_count=6 count
RESULT overall_asymmetry_confirmed=1 bool
```
Matches the reported value exactly (`overall_asymmetry_confirmed=1`, all sub-counts identical). load1≈24 during this run (shared box, quoted per house rules, not gated); count-only metric, immune to contention.

**My own harness** (`v1_finite_boundary_binary.py`), a different platform pair and a different data key than the finder used (`binary_sensor.py`'s `WoodCheaperBinarySensor.extra_state_attributes["sek_per_kwh"]` against `coordinator.data["wood_fuel"]["sek_per_kwh"]`, vs. the finder's `climate.py`/`current_price`):
```
RESULT binary_sensor_class=WoodCheaperBinarySensor name
RESULT null_control_ok=1 bool value=0.42
RESULT binsens_leaks_nonfinite_nan=1 bool value=nan
RESULT binsens_leaks_nonfinite_inf=1 bool value=inf
RESULT binary_sensor_finite_call_count=0 count
RESULT binsens_asymmetry_confirmed=1 bool
```
Metric definition: `binsens_leaks_nonfinite` = 1 iff `WoodCheaperBinarySensor.extra_state_attributes()["sek_per_kwh"]` fails `orjson.dumps` once `coordinator.data["wood_fuel"]["sek_per_kwh"]` is non-finite. Confirms the asymmetry independently of the finder's chosen key/platform, so this is not an artefact of `current_price`/climate specifically — it is structural: `entity.py`'s `HeatPumpOptimizerEntity` (the shared base every platform subclasses) has no scrub, and `__init_subclass__` (sensor.py:327) is declared on `HeatPumpOptimizerSensorBase`, which only `sensor.py`'s classes subclass.

**Method attacks:**
- *Contention*: this is a count/bool metric (orjson success/failure, grep counts), not timing — contention does not apply. Final, not provisional.
- *Gate mode*: not a suite-gap claim; N/A.
- *Grid artefact*: N/A, not an aggregate.
- *Null control*: present and passing in both harnesses (finite value round-trips identically through both platforms).
- *Reachable in real HA, not just the stub*: `FakeHass.async_add_executor_job` runs inline, which the README's Traps section warns invalidates *executor-boundary* timing measurements — it does not affect this finding, which never touches the executor; it constructs real entity objects via the real `async_setup_entry` and reads real properties. The consequence (`orjson.dumps` failure) is what HA's own websocket/state-diff serializer would hit in a live install; this is real, not a stub artefact.
- *Trap in `verifier.md`/README* ("`HeatPumpOptimizerSensorBase.__init_subclass__` wraps every subclass... deleting a per-sensor guard will not reproduce a non-finite publish"): irrelevant here — no per-sensor guard was deleted; the finding is about platforms that were never wrapped by that class-level scrub at all, which I confirmed by reading `entity.py` and grepping `climate.py`/`switch.py`/`binary_sensor.py`/`datetime.py` for `class HeatPumpOptimizer.*Base`/`__init_subclass__` (none found) before running any harness.
- *Severity*: earned. A NaN/Inf in `coordinator.data` (e.g. from an unclamped external reading, a divide-by-zero on a zero-price interval, or a solver diagnostic) is plausible in production, and the consequence — an unhandled `orjson.dumps` exception path on climate/switch/binary_sensor/datetime attribute serialization vs. a silent `None` on the identical sensor key — is a real behavioral split with no test coverage naming it.

**Vote: verify.** Severity: **high** (as claimed) — confirmed with the finder's own harness and independently with a second platform/key pair; the mechanism is structural (a missing base-class hook, not a one-off), the null control passes, and the consequence is real (unhandled non-finite serialization on 4 of 5 entity platforms).

---

## D8-s2-01 — entity IDs not sorted alphabetically in `async_setup_entry`

**Re-run of finder's harness** (`s2_ordering_finding.py`, verbatim):
```
RESULT entity_ordering_violations=57 count
RESULT percentage_out_of_order=98.3 percent
RESULT total_entities=58 count
RESULT thread_factor=1.00 ratio
RESULT load1=24.08 load
RESULT swapins=0 count
```
The number reproduces (57/58, modulo the harness's own off-by-one between the two extraction passes — `total_entities` counts all classes with `_attr_entity_registry_enabled_default`-eligible names found by regex, 58, while my construction count below is 59; not investigated further since the whole metric is rejected on method grounds, see below).

**Method attack — this is the decisive one.** The harness's `metric_definition` is "count of position mismatches between actual entity_id order and alphabetical sort order," but the "actual" order it uses is *not* `entity_id` at all — it is the position of each `Entity(...)` constructor call inside the Python list literal in `sensor.py`'s `async_setup_entry` source text (via `ast.walk`), mapped back to `translation_key`. That is a source-code authoring convention with **no runtime path to a user**: `async_add_entities()`'s call order does not control Home Assistant's entity list, device page or dashboard ordering (those are sorted by the frontend, by name/entity_id, independent of registration order), and nothing in this card (`heatpump-optimizer-card.js`) or `tests/card.mjs` reads `async_setup_entry`'s list order either — confirmed by grep (no reference to construction order anywhere in the card).

The D8 brief's actual requirement is "grouping and naming such that alphabetical sort clusters related entities" — i.e., a property of the `entity_id` *strings*, not of the Python list. I wrote `v1_ordering_refute.py`, which builds every sensor through the real `async_setup_entry`, reads the entities' **actual constructed `entity_id`s**, and checks the brief's real claim directly:
```
RESULT total_entities=59 count
RESULT family_splits_in_construction_order=14 count
RESULT family_splits_when_actually_sorted=0 count
RESULT sort_invariant_to_construction_order=1 bool
RESULT brief_requirement_met=1 bool  (alphabetical sort of the real entity_id
values clusters every family contiguously, independent of async_setup_entry's
list literal order)
```
Metric definition: `family_splits` = number of entity_id "family" prefixes (the token after `heat_pump_optimizer_`, e.g. `cost`, `dhw`, `plan`) that are non-contiguous once the *actual* `entity_id` values are sorted alphabetically. When entities are taken in construction order, 14 families are split (matching the flavor of the finder's number) — but once you do what the brief says ("alphabetical sort") to the string the brief names (`entity_id`), the split count is **0**: every family clusters perfectly (e.g. sorted: `cost_baseline`, `cost_contract_comparison`, `cost_current_electricity_price`, `cost_monthly_peak_power`, `cost_power_headroom`, `cost_predicted`, `cost_total_heating` — all contiguous). The null control (`sort_invariant_to_construction_order=1`) confirms this is not sensitive to registration order at all, by construction of `sorted()`.

- *Contention*: N/A, count metric.
- *Gate mode*: N/A.
- *Grid artefact*: N/A.
- *Null control*: the finder's harness has none — it never checks whether its "actual order" (source list position) has any behavioral effect. That absence is the bug in the finding.
- *Reachable in real HA*: no. Source-list construction order is compile-time; it has no user-facing reachability at all. This is the strongest form of "wrong gate"/"stub-only" attack: the measured quantity isn't even a stub artefact, it's a static-analysis artefact of a metric that doesn't correspond to anything HA does.
- *Severity earned by consequence*: none. The thing the brief actually cares about (alphabetical `entity_id` clustering, which is what a user or the frontend would ever see) is already satisfied (0 splits).

**Vote: refute.** The finding conflates Python source list order with `entity_id` alphabetical order; the metric it reports has no runtime consequence, and the brief's actual requirement (entity_id strings cluster by family when sorted) is already met (`family_splits_when_actually_sorted=0`). Not a style nit worth a "weaken" either, since reordering the `async_setup_entry` list literal would change nothing a user experiences — the sole remaining possible motivation ("readability of the source list") is not what either the finding or the brief claims.

---

## D8-s2-02 — DHW temperature disabled by default but used in card

**Re-run of finder's harness** (`s2_enabled_analysis.py`, verbatim): confirms `value=1` — `DHWTemperatureSensor` has `translation_key` containing `dhw_temperature`, `_attr_entity_registry_enabled_default = False`, and `tests/card.mjs` contains a reference to `sensor.heat_pump_optimizer_dhw_temperature` (a local test constant, `TANK`). Reproduced.

**Method attack.** I read `sensor.py:1219-1240` and the production card (`custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`, not the test file the finder's static grep used) to check what actually happens when the entity is disabled:
- `DHWTemperatureSensor` carries an explicit code comment: *"Hot water is on from the tank volume alone, but the tank thermometer is an optional probe most installs never configure; unavailable without it, so disabled rather than shipped dead (#1335)."* This is the identical, deliberate pattern used for `WoodCheaperBinarySensor` (same issue number, same rationale) elsewhere in this round's own findings — which nobody flagged as a defect.
- The production card resolves the live-probe overlay via `plan.statNumber("_dhw_temperature")` → `plan.statEntity(...)`, which derives the candidate id `sensor.heat_pump_optimizer_dhw_temperature` and looks it up in `hass.states`. When the entity is disabled (absent from `states`), `statEntity` returns `null` and `statNumber` returns `null`.
- `overlayDhwDisplay(dhwFc, {probe, ...})` explicitly guards `if (probe != null && ...)` — when `probe` is `null` it skips the live-point overlay entirely and returns the forecast series (`dhwFc`, sourced from the always-published DHW **plan** sensor, not from `DHWTemperatureSensor`) unmodified. This is a designed graceful degradation, not a crash or a missing series: the DHW band/forecast chart still renders from the plan sensor regardless of whether the optional temperature-probe entity is enabled.
- `README.md` has zero mentions of `dhw_temperature`/enabling it, so there is no first-hour guidance promising this entity either — weakening the "card attempts to display it [and fails]" framing further.
- *Severity earned by consequence*: the actual consequence of the default is: a user without a configured DHW tank thermometer sees the DHW forecast band without a live-probe marker overlaid on it — exactly the intended behavior for an "optional probe, unavailable without it" entity, matching the same disabled-by-default pattern used deliberately elsewhere in this codebase.

**Vote: weaken.** The factual premise (entity disabled by default, referenced by the card) is correct and reproduces, but the claimed consequence ("fresh installs lack this entity when card attempts to display it") is not borne out — the card degrades gracefully by design, mirroring an identical, intentional pattern (#1335) applied elsewhere without objection. I would give this **low** (informational), not the finder's medium: worth a doc/comment cross-reference at most (e.g., noting in the card or README that the live-probe overlay needs the DHW temperature entity enabled), not a functional defect.
