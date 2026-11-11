# D6 round 4 — verifier 3 of 3 (re-run seat)

Worktree `../audit-r4-verify-D6-3`, detached at `0855277` (branch head of
`claude/13-dimension-audit-920935`). Findings were measured at baseline
`7dd68dd`; `git diff 7dd68dd..HEAD` touches none of the measured material —
the only package changes are `manifest.json` (6.4.2 → 6.4.3) and the card's
version string, and `docs/architecture.md`, `docs/automations.md`, `README.md`
and every module the harnesses import are byte-identical. **No finder number
moved.** (One claims-table row re-stamps itself when the harness is re-run
here: C42 reads 6.4.3 at the head, 6.4.2 at baseline, and C108/C109's
"removed by the export" links resolve in this full checkout — environment,
not contradiction. The committed `claims.json`/`claims.md` were restored
after my re-run.)

Every number below is a count or set comparison; `load1` during my runs was
2.8–7.2 with other agents on the box and none of these metrics touch it.

## D6-01 — architecture.md stale in ten claims, including the HA boundary — VERIFY (high)

**Finder's harness re-run** (`ha_boundary.py`, dynamic import-refusal probe,
empty `__init__` scratch copy): `modules_total=56`, `ha_free_import_failures=21`,
`undocumented_ha_dependents=11` — exactly the reported values.

**My own method** (`verify03_own.py`, written for this seat): a *static* AST
scan — top-level `ast.Import`/`ast.ImportFrom` of `homeassistant` per module,
with the doc's ten names hard-coded from my own reading of the sentence
rather than regexed out of it. Independent of the finder's subprocess probe
in both direction and mechanism:

    RESULT v3_modules_on_disk=56
    RESULT v3_ast_ha_importers=21
    RESULT v3_undocumented=11
    RESULT v3_option_pages=21          (len(config_flow._OPTION_PAGES), imported)
    RESULT v3_services_in_yaml=12      (PyYAML top-level keys of services.yaml)
    RESULT v3_switches_constructed=4   (real async_setup_entry, names via strings.json)
    RESULT v3_binary_sensors_constructed=5

The 21 importers and the 11 outside the doc's ten are the *same sets* both
ways. The census claims reproduce too: switch constructs Away / Boost Hot
Water / Boost Space Heating / Optimizer Active (doc: "Optimizer Active"
alone); binary_sensor constructs five incl. `Wood Cheaper Than Heat Pump`
(doc names four). The full `claims.py` table re-ran clean: 125 checked,
12 false, of which exactly 10 sit in architecture.md (C29, C32–C38, C40, C41).

**Attacks.**

- *Wrong gate mode* — not applicable (no mutant or golden number in the
  finding), but the embedded test-gap claim ("nothing pins
  architecture.md") I attacked by execution: `python3 tests/closure.py
  select --files docs/architecture.md` → `MODE: SCOPED -- 0 script(s) run`,
  while the same command for `README.md` selects `tests/entities.py`. The
  killing mutation lives in `docs/architecture.md` itself (e.g. line 8
  "45 modules" → "46 modules"): no gate script runs on that file, so nothing
  can notice. `docs/` is in `closure.py`'s `INERT` tuple (read at
  `tests/closure.py:184`), and a repo-wide grep finds no script outside
  `tools/audit/` that opens `architecture.md`. The gap is real and executed.
- *Aggregate artefact* — no grid to collapse; each of the ten claims is a
  separate sentence, and I re-derived six of the ten by my own methods above.
- *Null control* — the finder's C39 ("sensor.py # 59 sensors") is measured
  true and listed for contrast; my census confirms 59/4/5 against the doc's
  59/1/4 — the check distinguishes.
- *Test stub vs real HA* — the boundary claim is about import-time
  dependence, which the subprocess probe measures with no stub at all; my
  AST scan agrees without executing anything.
- *Severity* — the scale in COMMON.md:60 reads `high` = "a user-visible
  defect **or a wrong published value**". Ten wrong published values in one
  file, the load-bearing one being the architectural boundary a contributor
  relies on when placing a new module (the doc's own justification — "each
  module can be driven directly by tests/features.py" — is false for 11
  modules). High is earned by the scale's letter. The counter-argument (no
  runtime consequence, contributor-facing file only) would put it at medium;
  I record it and stay with high.

**Vote: verify, high.** Metric: package modules whose import fails with
`homeassistant` refused (finder) / top-level AST HA imports (mine) = 21,
of which 11 outside the ten the document names.

## D6-02 — Sensor-Gap Euro Advisor documented `CUR`, publishes no unit — VERIFY (medium)

**Finder's harness re-run** (`currency_unit.py`): `sensors_constructed=59`,
`currency_rows_documented=9`, `currency_rows_without_unit=1` (Sensor-Gap
Euro Advisor), `currency_sensors_with_unit=8`, with
`coordinator.currency = SEK`, `native_value=0.0, unit=None`.

**My own method**: I instantiated the classes *directly* with a coordinator
stub of my own (`currency="EUR"`, empty data), resolved each README `CUR`
row's class by AST over `sensor.py`'s `super().__init__(..., key,
translation_key)` calls, and read `native_unit_of_measurement` through the
stub `SensorEntity` property (same `_attr_` forwarding as real HA):

    RESULT v3_currency_classes_checked=9
    RESULT v3_currency_sensors_without_unit=1   (Sensor-Gap Euro Advisor, native_value=0.0)

Null control present both ways: the eight siblings (Predicted Savings,
Predicted Cost, Baseline Cost, DHW Heating Cost, Monthly Savings, three
lifetime costs) all answer `"EUR"`/`"SEK"`.

Source confirmation, independent of any harness: `SensorGapAdvisorSensor`
(`sensor.py:2563`) declares `_attr_state_class = MEASUREMENT`,
`_attr_suggested_display_precision = 0`, a `native_value` in currency per
month, and **no** `_attr_native_unit_of_measurement` anywhere — all 38
occurrences in `sensor.py` belong to other classes (the sibling monetary
sensors set `coordinator.currency` at 487, 510, 573, 589, 1247, 1790), and
`HeatPumpOptimizerSensorBase` (`sensor.py:277`) sets none either. README
row (`README.md:470`) reads `| Sensor-Gap Euro Advisor | CUR | …`, and the
entity's own name and docstring ("estimated extra €/month") promise money.

**Attacks.** *Aggregate/stub*: the census path drives the real
`async_setup_entry`; my direct instantiation removes the platform harness
entirely — same answer. *Reachability*: a missing class attribute is not
stub-dependent; real HA's `native_unit_of_measurement` forwards to the same
`_attr_`, so the state renders unitless in any install. The one sub-claim I
could not execute is the *long-term-statistics* wording — the recorder's
treatment of unitless MEASUREMENT sensors is real-HA behaviour no harness in
this tree can run; it is secondary (the bare-number rendering and absence of
currency conversion stand on their own) and does not carry the verdict.
*Severity*: medium fits — user-visible metadata defect, the numeric value
itself is right, workaround is the `gaps` attribute; "do not inflate".

**Vote: verify, medium.** Metric: README `CUR` rows whose constructed
entity's `native_unit_of_measurement` is None = 1 of 9.

## D6-03 — automations.md's fuse precondition not enforced; tariff alone makes headroom available at 0.0 kW — VERIFY (low)

**Finder's harness re-run** (`headroom_availability.py`): `cells=4`,
`available_cells=3`, `available_without_a_fuse=1`; the offending cell reads
`available=True, value=0.0, limit_source='capacity tariff with no peak
reference yet'`, both fuse cells `13.8 kW / main fuse`, the empty cell
unavailable.

**My own method** (`verify03_own.py`): same 2×2 grid but over a coordinator
I compose myself, reading both the `_power_headroom()` view *and* a real
`PowerHeadroomSensor` constructed over that coordinator's own
`_build_data_dict()`, with the hastub clock **frozen** at
`2026-01-01T00:10:00Z` — the first metering window of a month — so the
result cannot be an artefact of when the run happened:

    RESULT v3_cells=4
    RESULT v3_available_without_fuse=1
    RESULT v3_headroom_value_no_fuse_tariff=0.0 kW

Null control: the no-fuse/no-tariff cell is unavailable in both harnesses —
the availability is produced by the tariff term, not by sloppy gating.

**Attacks.** *Reachability in real HA* — the strongest available attack, and
it fails to refute: the tariff toggle (`grid` page, `config_flow.py:1511`)
and the fuse (`grid_connection` page, `config_flow.py:1520`,
`_number(0, 125, 1, 'A')`, default `DEFAULT_MAIN_FUSE_A = 0`) live on
different options pages with no cross-field validation (the only tariff
errors in config_flow are `invalid_peak_months`/`invalid_peak_hours`);
`main_fuse_amperes`' own help text says "0 leaves it unconfigured". The
branch is not merely reachable but deliberate — `coordinator.py:7528-7544`
documents it in as many words ("It used to be no answer at all … the fuse
defaults to 0"), and with the default empty months/hours masks
`tariff.sample_factor()` returns 1.0 at every real clock time
(`tariff.py:122-140`), so my frozen-clock run and any live install agree.
*Aggregate artefact* — a complete 2×2 grid, nothing to drop. *Stub* —
availability flows from the coordinator's data dict, which my entity read
from the real coordinator's own `_build_data_dict()`; `PowerHeadroomSensor.
available` (`sensor.py:2203`) is `super().available AND data["available"]`.
*Severity* — documentation-only, `limit_source` discloses the cause; low is
right and honestly priced.

**Vote: verify, low.** Metric: no-fuse cells of the (fuse × tariff) grid
where the headroom view and entity both report available = 1 of 2 (doc
predicts 0).

## Perturbations (all re-run, all move as stated)

| harness | arm | movement |
|---|---|---|
| `ha_boundary.py` | `HPO_D6_PERTURB=1` | failures 21→22, undocumented 11→12 |
| `currency_unit.py` | `HPO_D6_PERTURB=1` | without unit 1→0, with unit 8→9 |
| `headroom_availability.py` | `HPO_D6_PERTURB=1` | available cells 3→2, without fuse 1→0 (doc rule becomes true exactly when the tariff is removed) |
| `verify03_own.py` (mine) | `HPO_V3_PERTURB=1` | AST importers 21→22 (in-memory patch of drift.py source), unitless 1→0, without fuse 1→0 |

## Notes for the judge

- My harness is `tools/audit/round4/D6/verify03_own.py` (uncommitted, like
  this report); its header carries the full contract block. One iteration
  note: its first run reported 4 unitless CUR sensors because my class
  resolver required the two `super().__init__` strings to match — the
  lifetime sensors pass `("space_cost", "space_heating_cost")`. That was my
  harness's bug, not a fourth offender; fixed, the count is 1.
- Root rule of every harness used here: working directory; all were run
  from this worktree's root.
- No timing-based evidence anywhere in this seat, so nothing is provisional
  under contention; every RESULT is a count.
