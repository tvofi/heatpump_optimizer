# D7 round 8: verifier v1 (the only verifier on this panel)

- Tree: /home/claude/audit-r8/seats/D7-v1 (a copy tree of baseline cdf82daabcfe3777d98b31489f36df5555ec9d82). The finders' evidence was copied in from seats D7-s1 and D7-s2 with `cp -rn`. No finder harness hard-codes a seat path, so none needed rewriting.
- Environment: PYTHONPATH=tests/hastub, all five BLAS variables set to 1, TMPDIR and HPO_PLANDATA under /home/claude/audit-r8/tmp/D7-v1.
- Machine: 4-vCPU shared container, load1 between 1.36 and 5.0 during the session. Every number below is a count or ratio, so none is timing-provisional. thread_factor was 1.000 on every in-process harness. The subprocess-driving s2_spot runs print 2.2 to 2.4, which is structural (drivers run as child processes) and carries no timing.
- One verifier carries both halves of verifier.md, so each finding below has two parts. First, the finder's harness re-run with its perturbation and null control. Second, a harness of my own (`v1_*`) with its own one-line metric, and the attacks, in verifier.md's order.
- Production files are unmodified. Every mutation was applied in memory (method wrap or source recompile, restored in `finally`) or in a temp copy under TMPDIR. This was checked with `diff -r` against the export at the end (see the last section).

## Mechanism map

- **D7-s1-01 and D7-s1-03 are two mechanisms on one path, not one.** s1-01 is the missing `_learning_frozen` consult in `_run_system_identification`, which lets contaminated nights be recorded and adopted. s1-03 is the unnamed early `return` in `_adopt_system_identification`, which hides a refusal. They compound: a contaminated night that the gate does refuse is published as `completed=True, reason='ok'` with its contaminated UA. My harnesses show 7 such nights (light_new defrost 1/2/3, typical_slab wood 2 kW and defrost 1/2/3). Each fix leaves the other defect's number unmoved:
  - The freeze fix aborts the night before `_finish`, so it removes those 7 but none of the clean silent refusals (light_new clean).
  - The naming fix names every refusal but still adopts the 13 contaminated nights.
- D7-s1-02 is a separate mechanism: `two_zone_enabled=False` is hard-coded in the sizer and the fit.
- D7-s2-01 and D7-s2-02 share a pattern (a structure.py metric keyed on bare names) but are different metrics with different code (`module_references` versus `SEAM_REGEXES`). They are not one mechanism.
- D7-s2-03 is independent.

---

## D7-s1-01: sysid ignores the learning freeze (verify, medium)

**Finder's harness, re-run:**
- `s1_learner_freeze.py`: sysid_contaminated_ingest = **4** of 4. The clean column reads 1 for all five learners, and house_heat_loss contaminated reads 0 of 4, both matching the finder.
- `--perturb`: **0**, clean arm still 1.
- `s1_sysid_contam.py`: admitted_contaminated = **4** of 12, clean fit error 0.000 %.
- `--perturb`: **0**.
- Per-cell values match the finder exactly: heavy_old wood -2.90 / defrost +6.47; typical_slab wood -1.35 / defrost +3.14.

**My own harness:** `v1_sysid_freeze.py`.
- Metric: over a magnitude sweep, count the experiment nights that the real FakeHass coordinator carries to a heat-loss scale write while `_learning_frozen(indoor, outdoor)` was non-None on at least one recorded tick. Also report the worst |adopted UA error|.
- Drive: the real coordinator, built from each preset's own config, driven tick by tick through the production `_run_system_identification` + `_adopt_system_identification`. It is not the stub gate the finder used.
- Contamination is applied twice, physically in the plant and as a production flag: `_external_heat_active` for unrecorded wood heat, `_pump_signals.defrosting` for undelivered step heat.
- Sweep: wood 0.5/1/2 kW in relax, wood 0.5/1/2 kW in step, defrost for 1/2/3 step ticks, over 3 presets = 27 nights.

**Result:**
- contaminated_adopted = **13 of 27**.
- Worst adopted error **+21.44 %** (heavy_old, 3 defrost ticks): **1 night past the gate's own ±10 % bar**.
- Null: clean_adopted = 2 of 3 with error 0.000 %. light_new is refused by its prior half-width on the clean night too, as the finder reported.
- `--perturb` (the abort-on-freeze wrap): contaminated_adopted **0**, clean still 2.

**Attacks:**
1. *Contention:* none; these are counts.
2. *Gate mode:* not applicable.
3. *Grid artefact:* two checks.
   - The finder's 4/12 is inside the ±10 % bar on every adopted cell, which looked like "bounded by design". My sweep refutes that bound: the error grows with the contamination dose (heavy_old defrost gives +6.05 / +8.75 / +21.44 % for 1 / 2 / 3 ticks).
   - Dropping the single most favourable cell (the +21.44 % one) still leaves 12 contaminated adoptions, worst +8.75 %.
4. *Null control:* present and passing in both harnesses.
5. *Reachability:*
   - `_run_system_identification` runs in `_async_update_data` right after the solve (coordinator.py:4960), and the flags I set are the ones the update path itself sets. No executor timing is involved, so the FakeHass trap does not apply.
   - Reachability depends on configuration. `_external_heat_active` needs external-heat detection configured, and `defrosting` needs a pump defrost signal. An install without those sensors is not protected by `_learning_frozen` either, so the fix covers only flagged intervals.
6. *Severity:*
   - Against: a persisted heat-loss scale off by up to 21 % from one armed night is bounded, and the passive learner keeps correcting afterwards.
   - For: the corruption is written to disk immediately (`_async_save_thermal_learning`).
   - That consequence fits **medium**, as claimed.

**Code read (context, not evidence):** the method checks only `space_blocked` and `freeze_reason` (coordinator.py:10441-10449), and neither covers defrost, external heat, ventilation or input health.

**Discrepancy:** none on the finder's numbers. My sweep extends them: the finder's "adopted error stays within 6.5 %" is not a property of the mechanism.

## D7-s1-02: the one-room sysid plant on a two-zone house (verify, medium)

**Finder's harness, re-run** (`s1_sysid_twozone.py`):
- twozone_admitted = **0** of 3 and singlezone_admitted = 2 of 3, matching.
- Cells match exactly: light_new aborts at 0.83 K, typical_slab at 0.91 K, heavy_old finishes at -5.66 % with hw=inf.
- `--perturb` (plant `two_zone_enabled=False`): **0 -> 2**, not the 0 -> 1 the finder reported. typical_slab is also adopted, at +0.01 %. The direction ("up") holds and the value in the finding is stale.

**My own harness:** `v1_sysid_twozone.py`.
- Metric: the count of two-zone presets for which ONE experiment night, driven through the real coordinator built from the preset's two-zone config, ends in a heat-loss scale write.
- The coordinator's indoor reading is the plant's `upper_floor_temperature`, as `_update_current_state` (coordinator.py:5223-5228) maps the sensor.

**Result:**
- twozone_adopted = **0** of 3. All three abort in the step phase: light_new at 0.828 K, heavy_old at 0.961 K, typical_slab at 1.288 K sensor excursion, against the 0.8 K allowance.
- On the real coordinator path heavy_old aborts, where the finder's stub path finished it and refused it at hw=inf. The count is the same.
- Null: singlezone_adopted = 2 of 3, with scale error ≤ 0.06 %.
- `--perturb` (plant single-zone, declared two-zone): **0 -> 2**, matching my re-run of the finder's harness.

**Attacks:**
- *Is the cause the sensor or the plant?* `--sensor avg` feeds the area-weighted `room_temperature` instead of the upper floor, and still gives 0 of 3 (two aborts; light_new finishes at +7.9 % UA and is refused). The failure is the one-room model of a two-zone plant, not only the thermometer choice.
- *Grid:* 3 cells; every one fails, so there is no favourable cell to drop.
- *Null:* passes.
- *Reachability:* the experiment arms on any plant with a non-degenerate slab pair (`slab_mode_identifiability`), and two-zone is a supported config. There is also a second inconsistency on the same path: `_run_system_identification` passes `house_ua = heat_loss_coefficient * scale`, while `_adopt_system_identification` divides by `upper + lower` on two-zone.
- *Severity:* the experiment is inert on every two-zone preset, and the abort fires only after the sensor has passed the comfort allowance, by up to 1.29 K against 0.8 K on typical_slab in my run. That is bounded cost with an obvious workaround (don't arm), so **medium** holds.

## D7-s1-03: the #1410 gate refuses silently (verify, medium)

**Finder's harness, re-run** (`s1_gate_silent.py`):
- silent_refusals = **10** of 19 finished, adopted 9, per-cell identical. heavy_old window publishes 0.5328 with completed=True, reason='ok'.
- `--perturb-fix`: **0**.
- `--perturb-bar`: **8**. Both match.

**My own harness:** `v1_gate_silent.py`.
- Metric: finished nights on the real coordinator where no scale was written, AND `coordinator._learning_view()["system_identification"]["result"]` (the published attribute) reads completed=True, reason="ok", AND the coordinator logger emitted 0 adoption-decision records.
- Nights: my 30-night sweep from v1_sysid_freeze.

**Result:**
- silent = **8** of 23 finished.
- Null control: adopted 15, and all 15 publish reason 'adopted' with 1 log record each.
- `--perturb` (the in-memory one-line edit that names the refusal): **0**, with the 15 adoptions unchanged.

**Attacks:**
- *Grid:* dropping light_new (4 of the 8) leaves 4 of 16 silent. That is independent of the finder's leave-one-out, which left 5 of 14.
- *Reachability:* the attribute is on the real learning view (coordinator.py:6818), not a stub.
- *A precision the finder did not state:* the night is not wholly silent in the log. `_finish` logs "System identification complete: ... UA=..." at INFO for each of these nights, so the log advertises a UA that was then refused without a word.
- *Severity:*
  - A published diagnostic that reads "completed/ok" for a refused result is close to COMMON's "wrong published value" (high).
  - But `reason` does differ from an adoption ('ok' versus 'adopted'), so a careful reader can tell, and no control value is affected.
  - I keep **medium** ("defect with a workaround").

## D7-s2-01: dead-code screen keyed on bare names (verify, low)

**Finder's harness, re-run:**
- `s2_reach.py --perturb --gate-probe`: unreachable_missed_by_gate = **12**, gate_dead_total = 0, perturbed 11.
- Gate probe: planting `describe` leaves the gate at 0; planting a unique name gives 1.
- `s2_sentinel.py`: prod_calls = 0 for both functions; test_calls are 10 and 1; logger_reads_total = 0.
- Controls: 14 / 69 / 5324.
- `--perturb`: prod_calls[grid_fee.is_valid_spec] = **14**, not 12 as stated. The direction holds. The perturbation rebinds `config_flow.is_valid_spec`, so it inherits exactly the control's 14 production calls. The finder's 12 is a stale or incidental difference, and the value in the finding should read 14. Also in the perturbed run: the dhw_schedule control drops to 0 as expected (its binding was replaced), and the coordinator logger count is 5325.

**My own harness:** `v1_dead.py`.
- Metric: of the 12 candidates, the count with ZERO module-qualified production references AND not listed by `structure.measure()`.
- A module-qualified reference is any of: `from .<mod> import <name>`; `<alias-of-mod>.<name>`; `getattr(<alias>, "<name>")`; or, for a private `_LOGGER`, a Name load in its own module.

**Result:**
- unreferenced_missed_by_gate = **12** of 12, gate_dead_top_level_symbols = 0.
- Null: 3 of 3 controls referenced (dhw_schedule.is_valid_spec 1, presets.derive 3, coordinator._LOGGER 123).
- `--perturb` renames `grid_fee.is_valid_spec` to a unique name in a temp copy: the gate goes **0 -> 1** and lists exactly that symbol. The symbol was "live" only through the name collision.

**Attacks:**
- *By design?* structure.py documents the screen as name-based and "a screen for accidental deadness, not a linker" (module_references docstring). The metric behaves as documented, so this is a reading of a carried metric (which D7.md allows) rather than a broken check.
- *Composition:* 10 of the 12 are one unused `_LOGGER = logging.getLogger(__name__)` line each. The two real functions total 26 lines, and both are test-pinned (is_valid_spec is called 10 times by tests, describe once), so removing them touches tests.
- **low**/hygiene is right, and the finder claimed low.

## D7-s2-02: seam rows track method names (verify, low)

**Finder's harness, re-run** (`s2_rename.py`):
- renames_that_lower = **27**, raise = 48, max drop 7, max cut drop 22, range 1..7.
- Without the top rename the max drop is 5. null_nonzero = 0.
- `--perturb` (empty SEAM_REGEXES): 0 for everything. All match.

**My own harness:** `v1_seam_rename.py`.
- Metric: for each method, the largest drop in `cross_seam_edges` achievable by renaming only that method into ANY of the six buckets, not only core. The rename is AST-level: the def plus every `self.<name>` Attribute.
- The measured baseline is 140 against a budget of 140, confirming the zero headroom.

**Result:**
- methods_with_drop = **51** of 227 (more than the finder's 27, because a rename may target any seam).
- max_single_rename_drop = **7** (`_commanded_power`), the same as the finder. max cut drop 23.
- Null (fresh same-bucket names): 0 non-zero.
- `--perturb` (empty SEAM_REGEXES): 0.

**Attacks:**
- *By design?* The partition is documented as "a method belongs to the FIRST seam whose regex matches its name ... part of the metric definition" (#193's plan of record). A rename does move a method between seams by definition, so a rename that lowers the row is also a real reassignment under the metric's own semantics.
- What the finding shows, and what I confirm, is that a zero-headroom ratchet can be paid for by renaming instead of decoupling. That is a Goodhart hole, not a miscount.
- **low** is right.

## D7-s2-03: the wood-coil DHW edge is unguarded (verify, low)

**Finder's harness, re-run** (`s2_spot.py`):
- `--only M3`: killed[M3] = **0**. On the no-.git copy, features.py goes baseline rc=1 failed=1 -> mutant rc=1 failed=1.
- `--null --only M4`: killed = 0.
- `--only M3 --closure --jobs 2`: killed = **0** across the 13 closure drivers: config_flow_steps, deployment_shape, doc_claims, entities, finite_boundary, golden, guard_pins, manual_plan, plan_view, solar_alignment, structure, typing_ruler, wood_advisor. With features.py that makes 14, as claimed.

**My own harness:** `v1_coil_edge.py`.
- (a) Seam probe: the production `topology.describe_setup()` for a two_tank_4way + DHW + wood-coil config publishes the ("wood_tank", "dhw_tank") edge. Baseline **1**, mutant **0**, so the mutation is observable in the payload the card draws and is not an equivalent mutant.
- (b) The features.py kill rule on a private copy gives killed_by_features = **0**.
- (c) `--perturb` drops a one-check driver asserting that edge into the copy: killed **0 -> 1**.

**Attacks:**
1. *Wrong gate mode:* env_drift.py (excluded by the finder) cannot catch it.
   - The five `coord_*` golden fixtures carry `setup_topology`, but none configures the coil. `dhw_coil` appears 0 times in them, and `["wood_tank", "dhw_tank"]` appears 0 times.
   - The `wood_coil` plan scenario does not capture `describe_setup`.
   - So `--all` does not change the verdict.
2. *The card tests:* `card.mjs` builds the coil edge by hand (`twoTank.edges.concat([["wood_tank","dhw_tank"]])`, card.mjs:2439 and :3175; card_rig.mjs:493) and never takes it from Python, so it cannot see the mutation.
3. *Correction to the claim's wording:* "the only dhw_coil check in the suite passes dhw_coil=False" is not exact. features.py:10524 does call `describe_setup` with `dhw_wood_coil_enabled: True`, but it asserts only the `heat_pump -> dhw_tank` edge. The gap stands and the sentence should be amended.
4. *Named mutation (verifier.md step 4):* `custom_components/heatpump_optimizer/topology.py`, `        if dhw_coil:` -> `        if False:` in `layout_edges`. The killing check would have to live in a test file, so the gap stands.
5. *Severity:* a missing pipe in the setup drawing, and no control consequence. **low** is right.

---

## Harnesses written by this seat

| harness | finding | command |
|---|---|---|
| v1_sysid_freeze.py | s1-01 | `PYTHONPATH=tests/hastub python3 -u tools/audit/round8/D7/v1_sysid_freeze.py [--perturb]` |
| v1_sysid_twozone.py | s1-02 | `... v1_sysid_twozone.py [--perturb] [--sensor avg]` |
| v1_gate_silent.py | s1-03 | `... v1_gate_silent.py [--perturb]` (imports v1_sysid_freeze) |
| v1_dead.py | s2-01 | `... v1_dead.py [--perturb]` |
| v1_seam_rename.py | s2-02 | `... v1_seam_rename.py [--perturb]` (about 6.5 min on this box) |
| v1_coil_edge.py | s2-03 | `TMPDIR=<private> ... v1_coil_edge.py [--perturb] [--skip-features]` |

## Tree hygiene

At the end, `diff -r` of `custom_components/` and `tests/` against the export was empty. The only new files are under `tools/audit/round8/D7/`.
