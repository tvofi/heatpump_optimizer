# RCA — class P6 (round 9): a consumer reads a key or field no producer writes, with a silent fallback

Seat: round-9 RCA, class P6, N = 5 (judge 5, sweep 12 instances). Starts beside F1.2; barrier lands in F1.10.
Baseline `1936d5ca` (v6.7.1); prototype cut from `origin/main` `db878b29`.
Prototype branch: **`handoff/r9-rca-p6` @ `aa2026b7`** (read back with `git ls-remote`). It is one file,
`tests/entities.py` (+511 lines, 0 production lines). It is a prototype for the F1.10 fixer to carry, not a PR.

---

## Root cause (for the class issue)

### Cause

Every P6 consumer reads through a lookup that has a silent fallback: `dict.get(key, default)` on
`coordinator.data`, a numeric `ThermalState` dataclass default, the frontend showing the raw key when a
label is missing, or `getattr(obj, name, None)`. Nothing records which keys the producer actually
writes. So at the consumer, a producer that is missing looks exactly like one that is present.

Most instances pass a guard. Each guard written after an earlier instance took its **universe from that
instance**, not from production: one entity, one fixture device, or a hand-written list. Siblings that lack
the same producer stay unguarded.

`git log` shows which side moved in each round-9 instance:

| instance | what happened, from `git log` |
|---|---|
| D14-s1-02 `horizon_hours` | Read added at `aa2677ba` (#129, 2026-09-01). The string `"horizon_hours"` has never been a key in `coordinator.py` at any commit (`git log -S`). The consumer was written against a producer that never existed. |
| D14-s1-02 `boost_calls` | Production hook added at `07bdc557` (#733, 2026-09-10) for `tests/harness.py:FakeCoordinator` only. The production `persist()` branch is skipped under every entity test. |
| D4-s2-01 | `prefill_device_unreadable` entered `options.error` at `1ba44e57` (09-17). The config twin page (`7d47e80e`, 09-19) returns it and never gained it. #1262 (`3c2374b3`, 09-20) labelled the preview for **one fixture device**: `len(preview_keys) > 6`. |
| D10-s2-01 | `auto` and `economy` have been presets since the initial release (`ec45dc4d`). No check reads offered modes. |
| D12-s1-01, D2-s1-51 | The defaults date from the initial release. #103 (`37efd623`, 08-29) fixed the *published* side. #368 (`f4c6a2d2`, 09-03) wrote this in `tests/entities.py` above `_D801_IN_SCOPE`: *"`_solve_snapshot` deep-copies the state as the MPC's initial condition -- that is a different finding (the optimizer plans against a tank it has never measured) and it is not what this fix claims to close."* That is D12-s1-01, named in the tree 23 days before round 9 found it. |

**Reproduced at `1936d5ca`** (venv314, `PYTHONPATH=tests/hastub`). All five findings' own harnesses reproduce
exactly:

| harness | result at `1936d5ca` |
|---|---|
| `p6_keys.py` | `p6_unproduced_reads=2`, `p6_undefined_getattr=1`, `p6_dangling_entity_ids=0` |
| `climate_presets.py` | `untranslated_presets_{strings,en,sv}=2`, `uniconed_presets=2` |
| `state_seed.py` | `A_omitted_dhw_distinct_init_values=1` vs `B_mapped=23`; `A_omitted_dhw_window_hours_below_min=6.25 h` |
| `prefill_config_strings.py` | `unlabelled_fields_en=3`, `untranslated_errors_en=1` |
| `dhw_sweep_outdoor.py` | `off_total_cold=14 of_14`, `worst_rel_err=0.527` |

### Class search: what else the same cause reaches, beyond the sweep

Each arm of the barrier derives its universe from production. Run at `1936d5ca` and at `origin/main`, the
counts are identical:

- **Flow error codes (arm E): 2 new, 2 more than the sweep.** `_prefill_errors` is called by the config
  flow's `async_step_device_prefill` save (`config_flow.py:2434`). It can return `flow_target_needs_two_zone`
  (`:2041`) and `silent_mode_window_too_short` (`:2045`). Neither is in `config.error` in any of the three
  catalogues. This was traced statically through the call chain; the save was not driven.
- **Pre-fill preview fields (arm F): 9 unlabelled, not 3.** The preview's keys are exactly
  `modbus_prefill.infer`'s output: 15 keys, read off `_hot_water({})`, `_plant({}, {})` and `_NAMED`.
  `config.step.device_prefill` lacks both label and description for 9 of them in all three catalogues. The
  6 beyond the sweep are `dhw_legionella_interval_days`, `dhw_windows`, `heat_pump_max_power`,
  `mixing_valve_write_target_kind`, `silent_mode_windows` and `space_setpoint_unit`. The options twin page
  is clean. Each key is reachable per `infer`, but none was driven with a device exposing its register.
- **Solve seeds (arm S): 8 numeric seed fields stay at the constructor default.** The install is the flow's
  own (no thermometer, hot water on), run through 2 solves with the clock advanced one step (15 min). The 8
  fields are room, slab, outdoor, upper, lower, buffer, solar and dhw.
  - **3 are instances:** `dhw_temperature` (D12-s1-01) and `slab_temperature` (the sweep's instance).
    `outdoor_temperature` is the third: D2-s1-51 named only the advisor, and the solve seed carries 5.0 as
    well. Whether the optimizer reads that seed field was not measured.
  - **5 are declared** in the prototype, each with its reason. `room`, `upper` and `lower` fall under
    tvofi's A3(e) ruling, which is contested by D8-s2-01 in F7.3. `buffer`: this install configures no
    buffer tank. `solar`: the run's clock is 00:00, where 0 W/m² is the truth. The same exploratory run with
    the 10-cycle D8-01 fixture (clock frozen) showed all 8 constant across 9 solves.
- **`_current_state.outdoor_temperature` has 9 more readers in `coordinator.py`** besides the advisor at
  `:2675`: lines `756`, `804`, `3562`, `3656`, `3774`, `3828`, `4257` and `4444`. With no outdoor entity
  mapped, all of them read 5.0 unless something gates them; none was driven. A fix at the producer covers
  all nine. A fix in the advisor covers one.
- **Payload keys (arm K), probes (arm G), offered modes (arm P), entity ids (arm B): nothing beyond the
  sweep.** K and B match `p6_keys` exactly: 2 of 214 reads, and 0 dangling of 75 built.
- **The arms re-find earlier rounds' escapes:**
  - `1e4e4b9e^` (R7 D8-01, #1460): K flags `house_power_series` and `heat_pump_power_series`.
  - `8c3a13c4^` (R6 D6-02, #1392, whose fix added no guard): B flags both blueprint ids.
  - `3c2374b3^` (#1262): F flags 90 raw entries, where 54 remain after it.
- **Not reached by any arm (residual, stated plainly):**
  - the card's JS reads of entity attributes;
  - `hass.data` keys;
  - nested payload paths (the sweep's 8 `A-conditional` reads stay unjudged, because K treats a producer
    literal anywhere as produced);
  - dynamic-schema builders other than `_prefill_schema`;
  - solar at any clock but midnight.

### Process state: **(c)**, the process was followed and did not produce the intended result

The fix protocol existed and each fix followed it: a failing test first, then a check that is green today
and pins its instance. `fixer.md` step 8 (`6bc932db`, 09-22, in force before #1460's fix `1e4e4b9e` on 09-23)
requires *"name a rule that enumerates the class's seams (a command, not a description), run it"*. Each rule
that got run was keyed to the instance:

- #1460, `tests/entities.py`: *"The seam rule this finding states, as a rule rather than an instance: every
  key the advisor reads must be a key the payload writes."* The recorder wraps **one** sensor,
  `SensorGapAdvisorSensor`. Beside it in `sensor.py`, `horizon_hours` was already unproduced: it is present
  at `1e4e4b9e^` and was re-found above.
- #1262, `config_flow_steps.py:device_prefill_preview_texts`: *"every previewed field has a label where the
  frontend looks"*, over one fixture device's resolution.
- The error-code check, since v4.1.0: *"Every error key used by the validators exists in all three string
  files"* is a **hand-written set of 6 codes**. This is the "key-set check that supplied the value it
  asserted" that `defect-root-cause.md` names.
- #368 scoped the solve seed out in a comment. It predates `finding-propagation.md` (`f4ed26c0`, 09-06),
  and that rule is forward-only, so nothing ever carried the comment.
- The ledger (`tools/audit/bugclasses.json` P6) has recorded `detector: null`,
  `detector_idea: "Static cross-reference of coordinator.data/hass.data reads…"` and `status: open` across
  18 instances.

Why the other states do not fit:

- Not (b): no step was skipped.
- Not (a): the protocol and the ledger existed. Exception: D10's offered modes had no check at all, which is
  (a) locally.
- Not (d) for the class. One sub-part is (d): the config label walk (`28568fba`, 09-17) renders each
  handler with `None`, and a two-submit preview page arrived two days later (`7d47e80e`, 09-19).

The (c) countermeasure is not a firmer instruction. It makes the universe mechanical, so that obeying
step 8 yields a class-wide check.

### Cost test

`cost(countermeasure, standing) < cost(defect) × P(recurrence)`, per round interval
(round 8 baseline `cdf82daa` → round 9 `1936d5ca`: 842 commits, 92 first-parent merges, 2.6 days).

- **P(recurrence), measured.** The ledger has 18 P6 instances over rounds 1–4, 6 and 7, and round 9 has 5:
  23 over 9 rounds, **2.56 per round**. Round 8's #1526 is marked "class P6" in `tests/features.py`, but the
  ledger has no round-8 row.
- **Cost per instance: a lower bound only.**
  - Elapsed time from branch to merge for the three P6 fix PRs I could date: #1417 28 min, #1576 2 h 02 min,
    #1273 2 h 19 min.
  - That excludes finding, verifying, judging and sweeping. One reproduction pass over round 9's 5
    harnesses costs 150 s (25.4 + 1.2 + 122 + 0.4 + 0.9).
  - Defect side: **≥ 72 min per round** (2.56 × 28 min), and 356 min at the slowest measured PR.
- **Standing cost, measured.** The P6 section adds 1.2–1.3 s of parent CPU per `entities.py` run. Wall
  time was 2.9 / 3.9 / 4.3 s at load1 8–9 on 4 cores, and ≤ 6.2 s at load1 16 before arm B was added. The
  solve runs in the worker process, so wall time is the honest figure. For comparison, `entities.py` itself
  took 129 s at one run and 258 s under load 16.
- **Runs per round interval: not measured.**
  - Central estimate: 92 PRs × about 4 runs, CI plus local, is roughly 370 runs × 4.3 s ≈ **27 min**.
  - Worst corner: every one of the 842 commits runs the gate twice at 6.2 s, about **174 min**.
  - Break-even at the adverse pairing (6.2 s against the 72 min floor) is about 700 runs per interval.
- **Verdict: passes** at the central estimate (27 min < 72 min floor). It fails only in the corner where
  every commit runs the gate twice at the heaviest load measured **and** every instance costs as little as
  the cheapest fix PR measured. That corner prices the defect without its find, verify and judge cost. It
  also ignores severity: D12-s1-01 is high, with `window_hours_below_min=6.25 h`. If tvofi prefers,
  arm S alone (the solve-driven part) can move to the nightly lane, which leaves the static arms at
  about 2 s.

### Countermeasure: the class-eliminating barrier (addresses state (c))

The form is one "every read has a producer" section in `tests/entities.py`, after the D8-01 section. It has
seven arms, and each takes its universe from production:

| arm | property checked | universe | exemption table (entries that stop matching are refused) |
|---|---|---|---|
| K | a `coordinator.data` key read in a platform, `diagnostics` or `__init__` has a producer literal | static: 214 reads | — |
| B | an entity id named in a blueprint default, the card or the package is built | runtime: 75 built | — |
| G | `getattr`/`hasattr` on a literal names something production defines | static: 259 probes | `P6_UPSTREAM_PROBES` (14 Home Assistant names, carried from `p6_keys`) |
| E | an error code a flow can return is in that flow's `error` table, in 3 catalogues | static, with call-site attribution and `*problem` validators: 18 codes | — (**replaces the hand-written 6-code set**) |
| P | a non-standard preset, fan or swing mode an entity offers is translated in 3 catalogues and iconed | static | `P6_HA_PRESETS` (Home Assistant's own) |
| F | every key the pre-fill preview can render has a label and a description, in both flows and 3 catalogues | `modbus_prefill` tables: 15 keys | — |
| S | no numeric solve seed equals its constructor default at every solve, in the flow's own install, over 2 solves 15 min apart on a 6 h horizon | runtime | `P6_SEED_DEFAULTS_DECLARED` (5, with reasons) |

A null-control check plants one defect per arm (K, G, E, F, P, B, S) and requires each to fire. Every
arm also asserts that its universe is non-empty, so no arm can pass by skipping.

**Demonstrations.** Every run is the section as committed, executed by
`scratchpad/run_p6_section.sh` (it runs `entities.py` through the end of the section).

| tree | K | B | G | E | P | F | S | null |
|---|---|---|---|---|---|---|---|---|
| `1936d5ca` (baseline) | FAIL 2 | ok | FAIL 1 | FAIL 9 | FAIL 8 | FAIL 54 | FAIL dhw, outdoor, slab | ok |
| `origin/main` + barrier (`aa2026b7`) | FAIL 2 | ok | FAIL 1 | FAIL 9 | FAIL 8 | FAIL 54 | FAIL dhw, outdoor, slab | ok |
| barrier + in-memory **stand-in** fixes (below) | ok | ok | ok | ok | ok | ok | ok | ok |
| `1e4e4b9e^` (R7 D8-01) | FAIL, incl. the 2 series | ok | FAIL | FAIL | FAIL | FAIL | FAIL | ok |
| `8c3a13c4^` (R6 D6-02) | FAIL | **FAIL 2 blueprint ids** | FAIL | FAIL | FAIL | FAIL | FAIL | ok |
| `3c2374b3^` (#1262) | FAIL | FAIL | FAIL | FAIL | FAIL | **FAIL 90** | FAIL | ok |

The stand-in fixes are **not fixes**. They were applied only in the scratch tree
`scratchpad/rca-p6-fixed`, to show the pass side before the instance PRs exist:

- publish `horizon_hours`;
- drop the `boost_calls` hook;
- add the 3 config error codes, the 9 preview labels and descriptions, and a climate translation key with
  preset states and icons;
- write outdoor from `forecast[0]` when unmapped;
- seed dhw and slab from the previous result's trajectory at step 1.

The healthy stand-in tree is silent. Several unrelated checks go red there because of the stand-ins'
crudeness: `_ctx` access, and the climate translation shape needs `name`.

**Ratchet.** The barrier adds 0 production lines and touches no `*_budgets.json`; `structure.py` measures
only `custom_components/`. `closure.py no-copies` passes. The `entities.py` closure already lists every
package file, `strings.json` and `icons.json`. Ruff findings on the file stay at the pre-existing 97.

---

## Plan fold

- **Landing PR: F1.10, as planned.** It is red until every P6 instance PR has merged: F1.2, F1.5, F5.2 and
  F1.10's own D14-s1-02. F1.10's `after` edges already reach them (F5.2 through F1.8).
- **F1.10's tvofi gate is not needed for P6.** D14-s1-02's boost half can drop the hook without touching
  `tests/harness.py`: patch `boost.persist` with a recorder inside `tests/entities.py`, where the three
  boost-switch checks live. Demonstrated in the stand-in tree: *"turning DHW/space boost on/off reaches the
  coordinator"* passes 3 of 3. `FakeCoordinator.boost_calls` stays for `async_set_boost`. If P2 and P3 do
  not need `harness.py` either, F1.10 can drop "Needs tvofi". That is the orchestrator's call; this seat
  cannot see those seats' forms.
- **Files:** `tests/entities.py` only. It is not code-owned and not policy. Estimate: **0 production lines,
  about 510 test lines** (423 excluding comments and blank lines). F1.10 may delete the hand-written
  6-code error check that arm E subsumes.
- **Carries into instance briefs.** By `finding-propagation.md`, the orchestrator writes these into each
  group's `brief`; this seat does not edit the roster:
  - **F5.2 (D4-s2-01):** the universe is 9 preview fields, not 3 (list above), each needing a label and a
    description in 3 catalogues. The config error table owes 3 codes, not 1: `prefill_device_unreadable`,
    `flow_target_needs_two_zone` and `silent_mode_window_too_short`. Control: arm F / arm E at 0.
  - **F5.2 (D10-s2-01):** arm P needs `entity.climate.<translation_key>.state_attributes.preset_mode.state`
    for `auto` and `economy` in 3 catalogues **and** `icons.json`. Setting `_attr_translation_key` also
    engages the translation-file checks: the climate block needs its `name`, as the stand-in showed.
  - **F1.2 (D12-s1-01):** the sweep's **slab** instance has no fix note. Arm S reads `slab_temperature` at
    22.0 on both solves, so F1.2 owes it with DHW. Watch the pinned premise *"with no tank sensor the
    published tank temperature is the model default"* in `tests/entities.py`: it holds after one light
    cycle, but a fix that also publishes the advanced seed will move it.
  - **F1.5 (D2-s1-51):** fix at the **producer**, by writing `outdoor_temperature` from the forecast's
    current hour when no outdoor reading is ok. The other 9 coordinator readers are then covered, and arm S
    clears `outdoor_temperature`. An advisor-only fix leaves S red on `outdoor_temperature`, and it may not
    be declared away without evidence that no other reader is ungated.
  - **F7.3 (D8-s2-01, tvofi's A3(e) ruling):** `room`, `upper` and `lower` are declared in arm S under
    A3(e). Whichever way tvofi rules, S's stale-declaration refusal forces the table to follow.
- **PR set and `after` edges:** no change.

## Needs tvofi

- A ruling to **keep, or move to nightly, arm S's solve** (about 1–2 s of the 2.9–4.3 s measured). The cost
  test passes at the central estimate; nightly is the cheaper form if the worst corner worries tvofi.
- Whether F1.10 **still needs tvofi** once P6 no longer touches `tests/harness.py`.
- No budget raise is needed.

## Evidence

- Branch `handoff/r9-rca-p6`: `95535695` (arms K, G, E, P, F, S and the null controls), then `aa2026b7`
  (arm B).
- Scratch (session-local): `rca-p6-base` (`1936d5ca` plus the harnesses), `rca-p6-fixed` (the stand-in
  tree), `hist-{1e4e4b9e,8c3a13c4,3c2374b3}` (pre-fix trees), `run_p6_section.sh`, `p6_arms.py` (the
  standalone static arms used for development).
- Harness reproduction runs, and the section runs quoted above, are in this seat's transcript. The numbers
  here are copied from those outputs.
