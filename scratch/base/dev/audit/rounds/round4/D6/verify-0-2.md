# Verifier 2 report — panel D6-0, round 4

Tree: worktree `audit-r4-verify-D6-2` at `0855277` (branch head; findings were
measured at baseline `7dd68dd` — **no number moved** between the two). Python
3.11.5 (`/Library/Frameworks/...`), `PYTHONPATH=tests/hastub`, run from the
worktree root. Stance: refute-first. I did not read other verifiers' output or
the register's verdict columns.

Every number in this panel is a count or a set comparison — contention-immune
by the resource rules. `load1` during my runs was 3.2–8.9 with other agents on
the box; `thread_factor=1.0` and zero concurrent `stress.py`/`run.sh`
processes at the final checks. No timing-based reasoning is used anywhere
below, so nothing here is provisional.

## Harness re-runs (finder's, exact commands from headers)

| harness | result | expected | match |
|---|---|---|---|
| `ha_boundary.py` | modules_total=56, documented_ha_modules=11, ha_free_import_failures=21, undocumented_ha_dependents=11 | same | exact |
| `ha_boundary.py` `HPO_D6_PERTURB=1` | failures 21→22, undocumented 11→12 | same | moves |
| `claims.py` (no `--links`) | extracted=125, checked=125, true=111, false=12, stale=0, unverifiable=2, defaults=76, ranges=76, arch 56/45/11, ha=21 | header's stated no-links variant | exact |
| `claims.py` `HPO_D6_PERTURB=1` | false 12→13, true 111→110 | same | moves |
| `currency_unit.py` | sensors=59, CUR rows=9, without unit=1, with unit=8; offender `Sensor-Gap Euro Advisor`, `unit=None, native_value=0.0`, currency SEK | same | exact |
| `currency_unit.py` `HPO_D6_PERTURB=1` | without unit 1→0, with unit 8→9 | same | moves |
| `headroom_availability.py` | cells=4, available=3, available_without_a_fuse=1, predicted=2; the no-fuse-tariff cell available=True value=0.0 `limit_source='capacity tariff with no peak reference yet'` | same | exact |
| `headroom_availability.py` `HPO_D6_PERTURB=1` | available 3→2, without fuse 1→0 | same | moves |

Root rule honoured: every harness uses `ROOT = Path(".")`; I ran them from the
worktree root, so they measured the tree under test, not the evidence tag.

## My own harnesses (all under `tools/audit/round4/D6/`, same root rule)

- `verify2_boundary.py` — AST scan of direct module-level `homeassistant`
  import statements (top level, incl. module-level try/if bodies; not function
  bodies) **plus** an import-refusal probe that *attributes* every failure to
  the refusal by walking the exception chain.
- `verify2_currency.py` — drives the real `sensor.async_setup_entry` census
  with a coordinator whose house-meter slot is empty and whose series/tariff
  make the advisor's figure non-zero, then reads `native_value` and the unit;
  control group = every README `CUR` row.
- `verify2_headroom.py` — the finder's 2×2 grid swept over five pinned clock
  instants (1st of month 00:30 and 14:00, 17th 03:00 and 14:00, a summer
  8 July 09:00) via the stub's `dt_util.freeze`.

## D6-01 — architecture.md stale in ten claims, boundary included

**Vote: verify (high, hygiene).**

My numbers: `v2_modules_total=56`, `v2_direct_ha_importers=21`,
`v2_probe_attributed_failures=21`, `v2_probe_unattributed_failures=0`,
`v2_undocumented_dependents=11`. The AST set and the probe set are *identical,
name for name* — every one of the 21 carries its own top-level
`import homeassistant`/`from homeassistant import …` statement (no
transitive-only members), and every probe failure's exception chain contains
the refusal marker, so no module failed for an unrelated missing dependency.
The finder's "21 modules import homeassistant at module level" is therefore
literally, not loosely, true — and the document says "exactly ten".

Independently re-derived sub-claims (my own commands, not the finder's
harness): 56 `.py` files vs "45 modules"; the module map lists 45 and omits
exactly `boost, datetime, dhw_learning, diagnostics, entity, legionella,
process_worker, repairs, services, setpoint_check, wood_fuel` (the finder's 11,
no more, no fewer); `config_flow._OPTION_PAGES` imported and counted = **21**
vs "13 option pages"; `services.yaml` top-level keys = **12** vs "the 11
services" (stated twice); `strings.json` switch names = **4** (`Away`, `Boost
Hot Water`, `Boost Space Heating`, `Optimizer Active`) vs a map that names
only "Optimizer Active"; binary_sensor names = **5** (the fifth `Wood Cheaper
Than Heat Pump`) vs the four the map lists; sensor count 59 = true as claimed.
That is ten false claims in the one file, matching the finder's table row for
row (`claims.md` C29, C32–C38, C40, C41).

Attacks, in the contract's order:

1. **Wrong gate mode** — not a test-gap claim; N/A. (I did confirm the
   finder's mechanism statement independently: no test reads
   `architecture.md` or `automations.md` — `grep -rn` over `tests/*.py` is
   empty — so nothing pins the file.)
2. **Aggregate artefact** — the "ten claims" aggregate is a per-claim verdict
   table; I re-measured seven of the ten with my own code. Dropping any single
   claim leaves nine false ones. Not an artefact.
3. **Null control** — the document's own named ten are the control: all ten
   named modules *are* among the 21 measured importers, so the error is
   omission (11 missing), not false accusation. The count direction is
   unambiguous.
4. **Reachability / stub distortion** — the strongest refute available here:
   `tests/hastub` provides a stub `homeassistant`, so one could argue the 11
   "can be driven by tests/features.py with no Home Assistant running" via the
   stub, rescuing the sentence's second half. It does not rescue the claim:
   the sentence's falsifiable core is "Exactly ten modules import
   `homeassistant` at module level", and my AST scan counts 21 *direct
   top-level import statements* in the production sources — a source fact,
   independent of any stub. My probe also refuses the real `homeassistant`
   package outright, which is stricter than the stub world. The claim is false
   under both readings.
5. **Severity** — `high` = "a wrong published value" per COMMON.md's scale.
   architecture.md's own header says it is "for anyone reading or changing the
   code"; its central invariant (the HA boundary) is off by 11 modules, 11 of
   56 modules are absent from its map, and its service/page/switch/binary-
   sensor counts are all wrong. Ten checkable false statements in the one file
   a contributor is told to trust, with the specific failure mode that a new
   module gets placed on the HA-free side in reliance on the boundary. Within
   the documentation dimension this is the top of the scale; `high` is earned
   against the ladder the other two findings of this panel set (one sentence,
   disambiguated = low; runtime metadata = medium; ten claims incl. the
   boundary = high).

**Metric definition I measured under**: modules under
`custom_components/heatpump_optimizer/` with a direct top-level AST
`homeassistant` import (21), minus the document's named set (10) → 11
undocumented; every number exactly reproducible, tolerance 0.

## D6-02 — Sensor-Gap Euro Advisor documented `CUR`, publishes no unit

**Vote: verify (medium, bug).**

My numbers (`verify2_currency.py`): `v2_gap_native_value=64.13` (non-zero — I
drove the coordinator with an *empty* house-meter slot, live series and a
45 currency/kW capacity tariff, so the advisor actually advises),
`v2_gap_unit=None`, `v2_gap_state_class='measurement'`,
`v2_gap_device_class=None`, `v2_cur_rows=9`, `v2_cur_rows_without_unit=1`
(`Sensor-Gap Euro Advisor`); the control group's other eight `CUR` rows all
publish `SEK`. The rendered state is a bare `64` with no unit, while
README.md:470 documents `CUR` and the description says "Estimated extra
€/month".

Method trust: I read the production sources rather than trusting the census.
`SensorGapAdvisorSensor` (sensor.py:2563) sets category, state class and
display precision — no unit; its `native_value` returns
`topology.rank_sensor_gaps(...)["sek_per_month"]`, a currency-per-month figure
(my run: `sek_per_month=64.13`, matching `native_value` exactly); the base
classes (`HeatPumpOptimizerSensorBase`, `entity.py`) set no unit anywhere
(`grep native_unit entity.py` is empty), while six sibling monetary sensors
each set `coordinator.currency` in `__init__` (sensor.py:487, 510, 573, 589,
1247, 1790 — the finder's line numbers check out).

Attacks:

1. **Wrong gate mode** — N/A; and I confirmed no test pins sensor units
   (`entities.py` pins values/categories but greps clean for a `CUR`-table
   unit check), so the finder is not silently re-reporting a suite gap.
2. **Aggregate artefact** — not a grid; a census with a control group.
3. **Null control** — the other eight `CUR` rows are the control and all pass.
   My own first control pass returned 0-without-unit and I traced it to a bug
   *in my harness* (a `"MISSING"` getattr default where absent-attribute means
   unitless); after the fix my number agrees with the finder's. The finder's
   filter was correct.
4. **Reachability in real HA** — the unit is an *optional* attribute in real
   Home Assistant (`SensorEntity.native_unit_of_measurement` resolves an
   absent `_attr_native_unit_of_measurement` to `None`), and the stub mirrors
   exactly that (`tests/hastub/homeassistant/components/sensor.py:119-120`).
   This is not a `FakeHass`-style distortion: the entity is constructed on
   every install by the real `async_setup_entry` (one of the 59), and with
   `state_class=MEASUREMENT` and no unit its long-term statistics are recorded
   unitless — the consequence the finder states holds in real HA.
5. **Severity** — the number is right, the unit metadata is missing, the
   `gaps` attribute carries the figures as a workaround: `medium` ("a defect
   with a workaround") is exactly right; not `high` (no wrong money is
   computed or acted on).

**Metric definition**: among the sensors the real `sensor.async_setup_entry`
constructs, those whose README Unit column reads exactly `CUR` while
`native_unit_of_measurement` resolves to None — 1 of 9, with a non-zero
currency-per-month value demonstrated.

## D6-03 — automations.md's Power Headroom precondition not enforced

**Vote: verify (low, hygiene).**

My numbers (`verify2_headroom.py`): over the 2×2 grid × five pinned clock
instants (20 cell-instants), `v2_available_no_fuse_pairs=5` — the no-fuse +
capacity-tariff cell is available **at every instant tested**, publishing
`headroom_kw=0.0` with `limit_source='capacity tariff with no peak reference
yet'`. The documented rule predicts 0. The finder's single-instant
measurement is therefore not an artefact of the hour it ran at: with default
tariff masks `CapacityTariff.sample_factor` is 1.0 at every instant, so the
falsification is time-robust (month-start night and day, mid-month, summer).

Attacks:

1. **Wrong gate mode** — N/A.
2. **Aggregate artefact** — a 2×2 grid is small but the claim is a universal
   ("stays unavailable until…"); one reachable counter-example cell falsifies
   it, and I strengthened it to five instants. Leave-one-out over instants:
   the verdict is unchanged by dropping any of them.
3. **Null control** — the no-fuse/no-tariff cell is the control and correctly
   reports unavailable at all five instants; the fuse cells correctly report
   13.8 kW. The grid separates the terms cleanly, and the finder's
   perturbation arm (tariff removed → doc rule becomes true) pins the tariff
   as the term the sentence omits.
4. **Reachability in real HA** — checked the configuration surface:
   `peak_tariff_enabled` is a plain boolean on the `grid` options page and
   `main_fuse_amperes` a plain 0–125 number defaulting to 0
   (`const.DEFAULT_MAIN_FUSE_A = 0`, `config_flow.py:1511/1520`), with no
   cross-validation requiring a fuse when the tariff is on. A real install
   that enables the tariff and never fills a fuse lands in the cell, and the
   coordinator's own comment (coordinator.py:7528–7544) names exactly that
   install as "the default, since the fuse defaults to 0". The entity's
   `available` is a faithful projection (`PowerHeadroomSensor.available`
   reads `data["power_headroom"]["available"]`, written by the real
   `_power_headroom()` at coordinator.py:6579) — no stub distortion.
5. **Severity** — documentation-only, no wrong money or comfort, and the
   sensor's own `limit_source` attribute says what happened: `low`, hygiene.
   Earned.

**Metric definition**: (cells, instants) in which the real
`HeatPumpOptimizerCoordinator._power_headroom()` answers `available: True`
with no main fuse configured — 5 of 5 no-fuse tariff instants, 0 predicted by
the document.

## Notes for the judge

- Nothing among the findings' numbers moved between baseline `7dd68dd` and
  branch head `0855277`: all three findings' numbers, including the finder's
  expected values in the harness headers, reproduce exactly. The only claims
  row that moved at all is C42, the manifest version (6.4.2 → 6.4.3 on the
  branch head), which stays **true**; C108's broken-link list is empty here
  because this worktree still carries `docs/audit-*.md`/`backlog.md` that the
  finder's export removed — also still true. C120/C121 differ by set
  ordering only. The emitted `claims.md`/`claims.json` in this worktree are
  regenerated from my clean (unperturbed, no `--links`) re-run.
- All numbers are counts/set comparisons; `load1` 3.2–8.9 quoted, not gated,
  and immaterial here.
- My harnesses carry `RESULT` lines, the thread pin, the working-directory
  root rule, and write nothing outside their own directory except a
  `tempfile.mkdtemp` scratch copy that is removed.
- The `README.md` "Sensor-Gap Euro Advisor" row and `docs/automations.md:18-20`
  were read directly; both say what the finder quotes.
