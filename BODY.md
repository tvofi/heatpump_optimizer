R10-SENSOR-PAYLOAD (round 10, wave 19). A sensor's payload number was read and guarded once per sensor, and the guards had drifted: `True` was published as 1, as `True` or as `None`, and a numeric string raised, passed raw or read `None` (D7-s2-60). This pull request gives that read one owner and one mixin, makes the finite scrub cover a mixin-supplied property (D7-s2-51), and gives the zone-setpoint renaming one owner (D7-s2-54).

Closes #2242. Part of #2238 (D7-s2-51, D7-s2-52, D7-s2-53, D7-s2-54 are done here; D8-s1-01 is not, see below).

What changed:
- `entity.payload_number(value, types)` is the one owner of "is this payload value a number a state publishes". It refuses bools (the mandate's bool policy: `True` is not a number), refuses text, and reads a numpy scalar as the Python value it holds. `sensor._as_float` now goes through it. `commanded_power_kw` reads both of its parts through it, and so does the climate entity's `current_temperature`.
- `sensor._PayloadNumberMixin` declares the read once: `_payload_path`, `_payload_digits`, `_payload_types`. 35 sensor classes use it in place of their own `native_value`. The rule: every class in `sensor.py` that subclasses `_PayloadNumberMixin`, less the mixin itself and the private bases `_AccumulatingSensor` / `_AccumulatingCostSensor` (37 with them). Those are the 21 value and section-path sensors, the 6 concrete accumulators (`_data_key` becomes `_payload_path`), and Measured Power, Observed COP, Monthly Peak, Valve Target, Comfort Weight, Optimization Score, Compressor Starts and Frequency Advisor. Their `_waiting_for` checks ask the same owner (`self._payload_number() is None`).
- `HeatPumpOptimizerEntity.__init_subclass__` resolves each published property through the MRO, so a mixin whose runtime base is `object` is scrubbed on each entity that inherits it. Only properties Home Assistant's own package owns are skipped. This replaces patch 00's package-module rule, under which an entity subclass defined outside the package published NaN (#2238's catch-up note). The carry required that case covered, and a test now covers it.
- `entity.zone_setpoint_attributes` owns the `upper_setpoint`/`lower_setpoint` renaming that climate, Current Setpoint and Heat Pump Action each spelled out (D7-s2-54).
- `entity.effective_outdoor(data)` replaces two copies of one rule. The first was `sensor._effective_outdoor(coordinator)`. The second was the climate entity's `_effective_outdoor` property, which had no guard and answered `None` where the sensor fell back to the forecast. The new function is pure and takes the payload. It also paid back the `coord_footprint` rise that the guarded read added to a function handed the coordinator.

Alternatives and why each lost (fixer.md step 17):
- Patches 01 and 02 as two mixins, a value mixin and a path mixin: a value is a path of length one, so two mixins would be the concept twice.
- Making `_SensorMixinBase` an entity subclass at runtime instead of resolving the MRO: that closes the sensor platform's instance only. The scrub's rule would still key on `__dict__`, and the next object-based mixin would escape it again.
- Patch 00's package-module filter: under it, the catch-up probe's `nan_published_outside_pkg` reads 1.

D8-s1-01 is not closed here. Its harness hit (`heating_now_while_off`) comes from `coordinator._build_plan_views`'s `active_now`, and its secondary count from `_plan_slots`'s 0.05 kW threshold. Both are in `coordinator.py`, outside this group's files and outside every seam in the architect notes. The `DHWScheduleSensor` fallback in `sensor.py` repeats `_plan_slots`'s threshold, which the #1644 checks pin. Changing the fallback alone would reopen D8-s1-02, the slot-count disagreement. So the fallback has to move together with `_plan_slots`. It is carried to R10-ARCH-SHAPES (see `## Forward-carry`).

## Head

a21ed7c29a8417b796789c8a2e6715fe9628703d

It builds on the bot pin commit 7e79b6762 by a plain descendant commit (no rebase); its parent chain holds the orchestrator's merges aac8c5e80 and fa1ecd8e1 of origin/main 99cf51c1a.

## Mutation proof

Run from a detached worktree at the head. Each mutant was run through `tests/finite_boundary.py`'s new arms (driver: seat scratch `run_new_arms.py`, which imports the script and calls `_no_rewrap_check`, `_scrub_mro_check` and `_number_state_arm`), then the file was restored.
- M1: `payload_number`'s predicate drops the bool test (`if not isinstance(value, types):`). Red: `every number state publishes None, never the bool or the text, from a bool or text payload (#2242)` (`BaselineCostSensor.native_value: True -> 1`, ...).
- M2: the scrub keys on `cls.__dict__.get(name)` again. Red: `a NaN native_value on a package mixin with runtime base object is published as None [published nan]`, and `an inherited scrubbed property re-exported by a subclass is not wrapped twice`.
- M3: the Home Assistant owner skip is deleted. Red: `Home Assistant's own native_value default is not wrapped by the scrub [vars=['native_value']]`.
- M4: `commanded_power_kw`'s space part is read raw. The census survived it, because the DHW sibling's guard masks it when every leaf is substituted at once. The arm added for it goes red: `commanded_power_kw refuses a bool or text part on either channel, and adds two numbers (#2242) [{'space True': 1.5, 'space text': 2.0}]`.
- M5: `effective_outdoor` reads the thermometer unguarded. Red: the number-state census (`CurrentCOPSensor.native_value: True -> 2.98`, `OutdoorTempSensor.native_value: '21.5' -> 21.5`).
- M6: climate's `extra_state_attributes` re-spells `attrs["upper_floor_setpoint"] = action["upper_setpoint"]`. `tests/entities.py` rc=1: `P2 owners: zone_setpoint_names is decided only by its owner ... [SEAM ['climate.py:272 in HeatPumpOptimizerClimate.extra_state_attributes']]`.

Round 1 (#2379 review, three sites surviving every driver after mutation-autofix, two advisory). `tests/finite_boundary.py`'s `_owner_pins` drives each through its production symbol; the driver is seat scratch `run_pins.py`, which calls `_owner_pins` alone. Every mutant below ran on a detached worktree at the head, and every row passes unmutated (`ALL 22 OWNER PINS PASSED`):
- `climate.py:140` GUARD_OFF (`if measured is not None:` -> `if False:`). Red: `climate current_temperature reads the measured upper floor first (#2379) [got 19.0, want 20.5]`.
- `entity.py:140` GUARD_OFF (`payload_number`'s `if isinstance(value, np.generic):` -> `if False:`). Red: `payload_number reads numpy.int64(7) as 7 (#2379) [got None, want 7]`.
- `sensor.py:2808` CMP_BOUND (`rate <= 0.0` -> `rate < 0.0`). Red: `_gap_energy_rate falls back to the contract price at a zero spot price (#2379) [got 1.0, want 0.8]`.
- Advisory, the upper/lower name swap in `zone_setpoint_attributes`. Red: `zone_setpoint_attributes keeps upper and lower apart (#2379)`.
- Advisory, Compressor Starts' `_payload_types = (int,)` deleted. Red: `Compressor Starts refuses a float count (#2379) [got 5.0, want None]`.

## Unpinned sites

`tools/pr/prepr.sh` step 6d lists them. The sites mutants M1 to M6 broke are killed by the arms named there; no other site's kill was measured locally, and CI's mutation job measures each. Seven pins were removed because they named lines this diff rewrote: `commanded_power_kw GUARD_OFF 75347d36` and `RETURN_DEL e75b38fb`; BufferTankTemp, ECL110EffectiveDisplace and SlabTemp `native_value` GUARD_OFF/RETURN_DEL; and `_as_float BOOLOP 992e85b6`, whose predicate is `payload_number`'s now. `mutation_table.completeness_problems` over the full inventory reads 0 at the head. `mutation-autofix` pins the new sites from CI's kill.

- custom_components/heatpump_optimizer/climate.py:140 GUARD_OFF: a value check, `tests/finite_boundary.py` `_owner_pins` (round 1; it survived every driver at 7e79b6762)
- custom_components/heatpump_optimizer/climate.py:145 GUARD_OFF: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/entity.py:61 GUARD_OFF: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/entity.py:65 RETURN_DEL: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/entity.py:95 GUARD_OFF: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/entity.py:97 GUARD_OFF: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/entity.py:100 GUARD_OFF: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/entity.py:102 RETURN_DEL: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/entity.py:140 GUARD_OFF: a value check, `tests/finite_boundary.py` `_owner_pins` (round 1; it survived every driver at 7e79b6762)
- custom_components/heatpump_optimizer/entity.py:142 GUARD_OFF: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/entity.py:144 RETURN_DEL: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/entity.py:239 GUARD_OFF: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/sensor.py:82 RETURN_DEL: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/sensor.py:366 RETURN_DEL: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/sensor.py:371 GUARD_OFF: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/sensor.py:373 RETURN_DEL: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/sensor.py:513 RETURN_DEL: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/sensor.py:664 RETURN_DEL: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/sensor.py:1694 RETURN_DEL: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/sensor.py:1701 GUARD_OFF: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/sensor.py:1900 GUARD_OFF: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/sensor.py:2368 GUARD_OFF: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/sensor.py:2764 GUARD_OFF: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/sensor.py:2795 RETURN_DEL: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)
- custom_components/heatpump_optimizer/sensor.py:2808 CMP_BOUND: a value check, `tests/finite_boundary.py` `_owner_pins` (round 1; it survived every driver at 7e79b6762)
- custom_components/heatpump_optimizer/sensor.py:2808 GUARD_OFF: pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)

## Null control

- Number-state census, the head's `tests/finite_boundary.py` at both ends. Base production 99cf51c1a: `number_state_escapes=42` over `number_states=37`. Head: 0 over 50. At the base, the reach arm also refuses (`unreached-unnamed=[BaselineCostSensor, ...]`), because seeding follows the `_payload_path` declarations, which the base's sensors do not have. The precondition arm refuses an unreached number-state sensor that `_NUMBER_STATE_COMPUTED` does not name (one entry: `PredictedIndoorTempSensor`, computed off the model).
- Scrub: the NaN on the entity class itself reads `None` at both ends. `probe_scrub_mixin.py`'s `nan_published_null=0` at the fork and at the head.
- P6 K extension: a planted `_payload_path = ("p6_no_such_key", "leaf")` is a seam (`a declared _payload_path naming an unwritten key is a P6 K seam (null control)`).
- P2 `zone_setpoint_names`: its planted sibling fails only that fact (the registry's null-control check).

## Figures

Fork 811df3cf3362ea0c626bcfdf8bf4a3cf2937c846, the merge base every figure below is measured against. The harness and archscore figures were taken at 9fae65a28829ad82d2be4ce5a56c64dcd10fec65. After that commit came the ledger deletions (10771e609), the `tests/closures.json` re-derivation for `tests/entities.py` (5923f6eb1, `./tests/derive_closures.sh --single tests/entities.py`), and a second main merge (839b1b863, merge base now 9a1ce39c3e901c814fceb015f09eec75f1a5ef5f). `git diff --stat 9fae65a28 839b1b863 -- custom_components` prints nothing. The main delta 811df3cf3..9a1ce39c3 touches `.github/workflows/tests.yml`, three delivery records and `tools/audit/seat/orchestrator_tick.py`: no production file and none of this diff's files. `tests/entities.py` was re-run at 10771e609 (`ALL 2348 ENTITY CHECKS PASSED`). Catch-up count: 2 main merges by this seat (91f1e35e6, 839b1b863), plus the orchestrator's merge fa1ecd8e1 of 99cf51c1a. The round-1 commit changes `tests/finite_boundary.py` alone. `tests/closure.py select --diff 7e79b6762` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (`tests/entities.py`, `tests/finite_boundary.py`). Both pass at the head: `ALL 2348 ENTITY CHECKS PASSED` and `ALL 101 FINITE BOUNDARY CHECKS PASSED`. 

Harnesses run from the baseline export. Each is a scratch copy whose only edits are `BASE = <ref>` and `REPO` pointed at the worktree:
- `dev/audit/rounds/round10/D7/arch-s2/shape_payload_guard.py` (sha1 e0b393e848040641033fcf25bea95ec34677f154). Fork: `implementations=35`, `guard_families=4`, `driven_sites=26`, `distinct_answer_vectors=5`, `disagreeing_probes=3` (`0,True,'21.5'`). Head: `implementations=6` (5 `_as_float` and 1 `round_if_not_none`: Outdoor Temperature, now guarded upstream by `effective_outdoor`), `disagreeing_probes=0`. This harness cannot see the mixin's property, because it has no literal path. The companion below applies the rule behaviourally.
- `dev/audit/rounds/round10/D14/sweep-P6/enumerate.py --tree` (sha1 d5898a4931e8ff946683f5552bdf7514f95d4255). The fork, as a `git archive` of 811df3cf3: `seams=56 instance=31 guarded=5 not_applicable=20`. Head (a `git archive` of the head): `seams=26 instance=0 guarded=6 not_applicable=20`. The seam count falls because the mixin sensors no longer carry a literal-path property. Every disposition is in the table below.
- Companion census `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` (`RESULT number_states` / `number_state_escapes`): the head's test at both ends: base 99cf51c1a 37 / 42, head 50 / 0. The 31 / 36 previously quoted came from an older copy of the test and is withdrawn.
- `dev/audit/rounds/round10/catchup/arch-s2/probe_scrub_mixin.py` (sha1 cc9cb65822c3281039aa83ab124c9032d172cf94). Fork: `mixin_supplied=0`, `nan_published=1`, `nan_published_outside_pkg=0`, `nan_published_null=0`. Head: `nan_published=0`, `nan_published_outside_pkg=0`, `nan_published_null=0`. The carry's requirement (outside-package 0 at both ends) holds.
- `dev/audit/rounds/round10/D7/arch-s2/scrub_escapes.py` (sha1 e67717a87b30d5f267cb3c6aeefdb884e797718c): `escapes=0` over `entity_classes=91` at both ends.
- `dev/audit/rounds/round10/D8/s1/f1_active_now.py`: `heating_now_while_off=1`, `slot_steps_declared_off=4` at 6e5753a4a and at the head. Unchanged by design: `coordinator.py` is not in this diff.
- `python3 tools/audit/archscore/score.py --diff 811df3cf3 HEAD`: `Architecture score: dS +5.6289 IMPROVES` (`duplication_copies 64 -> 41`, `coord_footprint 2547 -> 2540`).
- `python3 tests/structure.py`: `duplication_copies` 33 -> 17, recorded in c15f92abf, whose commit message names the rows.
- `GOLDEN_MODE=drift GOLDEN_REF=811df3cf3 python3 tests/golden.py`: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`. The goldens are byte-identical at the fork, so the golden rule holds and nothing is claimed.

Step-8 dispositions. The rule is `enumerate.py` at the fork; every seam it returns is listed here:
- Closed in this diff, routed through `_PayloadNumberMixin` / `payload_number` (31 instances):
  - PredictedSavings, SavingsPercentage, PredictedCost, BaselineCost, CurrentPrice
  - IndoorTemp, SolarIrradiance, SlabTemp, UpperFloorTemp, LowerFloorTemp, FloorReturnTemp
  - SolarHeatGain, BufferTankTemp, DHWTemperature, DHWHeatingCost
  - ECL110Displace, ECL110EffectiveDisplace, MeasuredPower, ObservedCOP
  - `_AccumulatingSensor`, MonthlyPeak, ValveTargetRecommendation, ComfortWeight
  - ContractComparison, PowerHeadroom, DHWSetpointAdvisor, MixedHotWater
  - OptimizationScore, CompressorStarts, FrequencyAdvisor
  - OutdoorTemp (through `effective_outdoor`)
- Already guarded (5): CurrentSetpoint, PredictionAccuracy, PVSurplus, ThermalBattery, ThermalBatteryEnergy. All go through `_as_float`, now `payload_number`'s.
- Not applicable (20): text, enum, timestamp or bool states, and the structured reads the sweep's notes name. Two of those structured reads still publish a number, and the census drives both:
  - CurrentPower, through `commanded_power_kw`: closed here.
  - CurrentCOP: closed here, through `payload_number` on the model's answer and `effective_outdoor`.

## Raise justification

n/a: no budget rises. `duplication_copies` falls and is recorded.

## Architecture score

Architecture score: dS +5.6289. No metric rises: `duplication_copies 64 -> 41` (the per-sensor reads replaced by the mixin, and the zone and outdoor rules each given one owner); `coord_footprint 2547 -> 2540` (the outdoor rule leaves a function handed the coordinator).

## Red checks

- `mutation`, red at 839b1b863 and at 7e79b6762: the unpinned-sites trigger. This branch removed 7 ledger pins whose lines it rewrote. Mutation-autofix pinned the killed new sites (7e79b6762). Three sites survived every driver: `climate.py:140` GUARD_OFF, `entity.py:140` GUARD_OFF and `sensor.py:2808` CMP_BOUND. Each now has a killing test that imports its production symbol (`## Mutation proof`, round 1), so none is triaged. This head's CI mutation lane is the authority, and I ran no local mutation table.
- Cheaper detector: none is owed. `prepr.sh` step 6d already listed all three as added-unpinned before the push, and my body disposed of them as "pinned by mutation-autofix" without measuring a kill. The gap was my disposition, not a missing detector. Countermeasure in this pull request: each site this diff added and that the census cannot single out is driven alone.
- `nightly-ha (stable)`, red at fe4d15d76 (job 117649075688), green at 60368fbac (job 117661672475). The two failed checks were `hb:positive_control` and `run:exit_status`, the second only the container's exit code following the first. The log line: `py-spy did not run: TimeoutExpired: Command '['/opt/hpo/py-spy', 'dump', '--nonblocking', '--pid', '1']' timed out after 30 seconds`. The control spun the loop for 600 ms, the stall detector read 600.2 ms and its own dump named the spin, and only the py-spy section was missing. The other 62 checks passed, including every `hb:` heartbeat arm, the entity roster and the payload arms. The cause is the runner environment, not this diff: this diff touches no file in `tests/nightly_ha.py`, the heartbeat code or `tests/requirements-nightly-ha.txt`, and `nightly-ha (2025.2.0)` passed on the same head. I did not establish why the attach stalled; a slow runner is the likely reason, and the green run at the next head on the same harness is consistent with that. I ran no local nightly-ha lane.
- Cheaper detector: none. The positive control is itself the detector of the heartbeat's ability to see a stall, and it fires only inside the real-Home-Assistant container. Standing cost of a retry-on-timeout around py-spy: up to a further 30 s on every run, and it would blunt a control whose job is to fail when py-spy cannot attach. No countermeasure is built here; the flake is outside this PR's scope and `nightly-ha (stable)` is green at this head.

## Forward-carry

D8-s1-01's remaining seams go to R10-ARCH-SHAPES, which #2380 landed in `dev/programme/rosters/wave-r10-groups.json`: `coordinator.py` `_build_plan_views` `active_now`, `_plan_slots`' 0.05 kW threshold, and the `sensor.py` `DHWScheduleSensor` fallback, which must move with `_plan_slots`.

## Friction

brief: contradiction: the roster brief locates D8-s1-01 in the "hot-water schedule sensor ... fallback", while the finder's harness hit is `plan_space_heating` through `coordinator._build_plan_views`; the fallback does not reach `f1_active_now.py`'s metric.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

