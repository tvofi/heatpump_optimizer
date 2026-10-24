# Round 9, D14 seat s1: classes P1 and P6

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1). Box B8: 4 cores, 15 GB, Linux,
CPython 3.14.0rc2 (`/home/claude/venv314`), shared with two other compute-heavy seats. Every
headline number here is a count, so contention cannot move it. The wall times in "Barrier cost"
are provisional.

Cells: `D14-s1` = steps M1 to M5, class axis {P1, P6}, every file (`check_scopes.py --seat D14-s1`
prints one line: `M1+M2+M3+M4+M5  P1,P6  (any file)`).

## Method

- **M1, the ledger.** In `tools/audit/bugclasses.json`, P1 has 12 instances over rounds 1 to 6
  and P6 has 18 over rounds 1 to 4, 6 and 7. Both have status `open`, `detector: null` and
  `barrier: null`.
- **M2, pick.** My scope assigns P1 and P6. P1 already has a partial in-tree barrier,
  `tests/finite_boundary.py` together with `QuarantiningStore`, but that barrier covers
  non-finite *numeric* leaves only. P6 has no enumerating detector: #1526 added a census for one
  slot shape only.
- **M3, detectors.**
  - `p1_store.py` seeds all 13 stores through their real writers. That seeding includes a taken
    snapshot, an applied manual plan, a held boost channel, the fuse advisor, a legionella cycle
    and the arbiter duty record. It then substitutes malformed values at every leaf and
    container of every store (4027 mutants). Each mutant goes through the real loaders, found at
    run time by recording which store key each loader reads. Then the real consumers run:
    `_build_data_dict`, `SnapshotRing.best_restore`, `async_restore_learned_snapshot`,
    `_roll_month` and every zero-argument saver. Last comes a 3-cycle `_async_update_data` wedge
    arm. The clock is frozen at an **aware** instant because Home Assistant's `dt_util.now()` is
    always aware. The hastub's default is naive (see Traps).
  - `p6_keys.py` has three arms:
    - A installs a recording dict as `coordinator.data`. It covers 5 golden topologies × 2
      cycles (the second with a real solve), every entity of every `PLATFORM_LIST` platform, and
      the diagnostics download.
    - B checks entity ids referenced in blueprint defaults, the card and the package against the
      ids the platforms build.
    - C lists `getattr`/`hasattr` calls on a literal that no production code defines.
- **Re-finds at pre-fix commits.** Each tree is a `git archive` of the parent commit, measured
  from its own root (the `harness.py` relative-path trap, below). Logs are under `runs/`.

| instance | tree | pre-fix | post-fix |
|---|---|---|---|
| R1 D1-01 (ledger lines/meta wrong shape) | `3511677a^` | `ledger.roll_month` AttributeError on lines/meta in {"x",3.0,[],null} | gone |
| R1 D1-05 (snapshot accuracy truthy non-dict) | `3511677a^` | `best_restore` AttributeError on "x", 3.0 | gone |
| R5 D1-05/06 (non-finite store leaves) | `b64c2f8c^` | p1_poison_mutants 453 | 410 (profile, curve-bias, draws and peaks seams gone) |
| R6 D1-01/02 (apply_cooling_rate, defrost duty) | `e299cd72^` | p1_poison_mutants 410 | 0 |
| R7 D8-01 (#1460 power series unwritten) | `1e4e4b9e^` | p6_unproduced_reads 6 | 2 |
| R6 D6-02 (blueprint default ids) | `8c3a13c4^` | p6_dangling_entity_ids 2 | 0 |

The ledger month-leaf `publish` escape, which #1518 closed at 93e3af05, is also re-found in the
`b64c2f8c` and `e299cd72` trees. It shows 0 at baseline.

## Findings

### D14-s1-01 (P1, medium, bug): a malformed persisted leaf still raises out of a loader or consumer, and one wedges every refresh

**Property.** No single-leaf malformation of any persisted store may raise out of that store's
loader or its downstream consumers, or fail an update cycle. A single-leaf malformation means a
non-finite value, a wrong type, a naive timestamp or the wrong container kind.

**Seam rule.** `PYTHONPATH=tests/hastub python tools/audit/round9/D14/s1/p1_store.py`, reading
the `SEAM escape` and `WEDGE` lines.

At baseline the detector reports `p1_escaping_mutants=11` over `p1_escape_seams=7` (clean
fixture 0), and `p1_wedged_seams=2` (the wedge null control fails 0 of 3 cycles). The seams:

1. **`dhw_legionella/last_cycle` and `last_attempt` hold a naive ISO timestamp.**
   `LegionellaTracker.hours_since` compares naive with aware and raises `TypeError` inside
   `_dhw_view`, so `_build_data_dict` raises. **3 of 3 update cycles fail with `UpdateFailed`**,
   and the naive value is written back unchanged, so a restart does not clear it.
2. **`boost/dhw/until` holds a naive timestamp.** `boost.restore` evaluates `parsed > now` and
   `TypeError` escapes the spawned `restore_session` task.
3. **`pump_duty/written` is not a dict, or a pair is `{}`.** `pump_arbiter._load` raises
   `AttributeError` or `KeyError`, because it catches only TypeError, ValueError and IndexError.
   It has already set `held.loaded = True`.
4. **`snapshots/#/accuracy/temperature_bias` is a string, a list or a dict.**
   `SnapshotRing.best_restore` calls `np.isfinite` on it and raises TypeError or ValueError, and
   so does the `restore_learned_snapshot` service, despite the docstring's "never raising
   (#D1-05)". This exact seam is present unchanged in the `3511677a` tree (2026-09-01).
5. **`snapshots/#/learners` is not a dict.** `_apply_learner_payloads` calls `learners.get` and
   raises `AttributeError`, so the service fails.

**Why the standing barrier missed them** (`--barrier` hooks `finite_boundary:_healthy_payloads`
and `finite_boundary:_leaf_paths`):

- `tests/finite_boundary.py` substitutes numeric leaves only, and its own seeding leaves no
  numeric leaf to substitute in `manual_plan`, `boost` and `away` (0 each). `snapshots` has 1.
- It drives only the loader and `_build_data_dict`.
- **`barrier_driven_escape_seams=0` of 7.**

**Perturbations.**

- `--perturb snapguard` removes `best_restore`'s isinstance guard, which re-opens R1 D1-05.
  Escapes go from 11 to 13 and seams from 7 to 8.
- `--perturb sanitize` turns `QuarantiningStore`'s scrub into the identity. Poison goes from 0
  to 388 and escapes from 11 to 18.

**Proposed barrier.**

- Move this detector's writer-driven seeding, all-leaf-kind substitution and consumer and wedge
  arms into `tests/finite_boundary.py`. The assertion would be `p1_escaping_mutants == 0` and
  `p1_wedged_seams == 0`, with its loader-count equality extended to the consumer set.
- Production fix scope:
  - One shared stored-instant parser that makes a naive value aware, used by every store
    timestamp read (`legionella.async_load`, `boost._parse_until`, `pump_arbiter._load`,
    `manual_plan.ManualOverride.from_dict`, the fuse-advisor read in `_maybe_run_fuse_advisor`,
    `away._parse_return_time`).
  - `_as_float` in `best_restore`.
  - An isinstance guard on `learners`.
  - Shape guards in `pump_arbiter._load`.

### D14-s1-02 (P6, low, hygiene): two payload reads that no producer writes, and one field only a test double writes

**Property.** Every key a consumer asks of `coordinator.data` is written by `_build_data_dict`
in at least one reachable configuration. Every attribute probed with a default is defined by
production code or by Home Assistant.

**Seam rule.** `PYTHONPATH=tests/hastub python tools/audit/round9/D14/s1/p6_keys.py`, reading
the `SEAM A-unproduced`, `SEAM B` and `SEAM C` lines.

At baseline:

- `p6_unproduced_reads=2`: `sensor.py:1482` and `sensor.py:1515` read `horizon_hours` with a
  24.0 fallback. No producer writes the key. The real horizon is
  `OptimizationConfig.horizon_hours`, which is never assigned, so the published value is right
  only by coincidence and cannot move with it. The seam is present in every tree measured back
  to `8c3a13c4`.
- `p6_undefined_getattr=1`: `boost.py:212` reads `getattr(coord, "boost_calls", None)`. The name
  exists only on `tests/harness.py:FakeCoordinator`, so every entity test that goes through
  `set_channel` skips the production `persist()` branch.
- `p6_dangling_entity_ids=0` of 75 built. The 8 conditional reads each have a producer literal:
  manual_plan, predictive_info.dhw_windows_resolved, valve_target_recommendation,
  contract_comparison.load_profile_value_per_kwh and wood_fuel.night_advice.

**Perturbation.** `--perturb` deletes the `_power_windows` line from `_build_data_dict`, in
memory and in the source that the static producer scan reads. Unproduced reads go from 2 to 5.
The self-test and clean fixture give 1 and 0.

**Proposed barrier.** Promote arms A, B and C to a `tests/` script, or into `entities.py`, with
`p6_unproduced_reads == 0 and p6_dangling_entity_ids == 0 and p6_undefined_getattr == 0`. Fix
scope: publish `horizon_hours` from `_opt_config` or drop the read, and replace the
`boost_calls` hook with a patched `persist` in the double.

## Non-findings

- `p1_poison_mutants=0` of 4027. With non-finite substitutes over every leaf of the 13 populated
  stores, including the snapshot ring's learner payloads that `finite_boundary.py` never seeds,
  nothing non-finite reaches live state or the payload. The documented `peak_threshold_kw` +inf
  sentinel is excluded.
- `store_constructions=13`, all of them `QuarantiningStore` (0 raw).
- 9 of 13 stores give 0 escapes: accuracy, away, dhw_draws, dhw_profile, energy, ledger,
  manual_plan, price_model and thermal_learning.
- Entity ids: 0 dangling across blueprint defaults, the card and the package. The legacy id in
  `notify_on_manual_plan.yaml` appears in prose only, not as a default.

## Barrier cost (M5, provisional)

- `p1_store.py`: 22 to 26 s wall single-threaded, measured at load1 1.2 to 2.5 with two other
  seats running, thread_factor 1.000.
- `p6_keys.py`: about 10 s.

Both should be re-taken in a quiet window.

## Traps met

- `tests/harness.py` inserts the relative paths `tests` and `custom_components`. A harness
  pointed at another tree while running from this root measures this root's package. Both
  harnesses therefore refuse to run unless cwd is the tree being measured.
- The hastub's `dt_util.now()` is naive when no clock is frozen, while Home Assistant's is
  aware. The stub's default makes an aware stored timestamp the malformed case, so the tests
  never meet the naive-stored case that production meets.

## Unfinished

- M3 (P6): no card JavaScript arm, which would check the attributes the card reads against the
  attributes entities publish.
- M3 (P1): no type-drift arm for boolean or string coercion. For example,
  `away.restore_override` takes `bool("false")` as True.
- M5: the barrier is proposed and costed, but not landed in `tests/`.

## Exposure

- `tools/audit/bugclasses.json`.
- Commit messages and stats for `3511677a`, `c4f8f213`, `e299cd72`, `8e5d1ace`, `b64c2f8c`,
  `df6e55f8`, `fd1a8528`, `93e3af05`, `2a451021`, `1e4e4b9e` and `8c3a13c4`, and archived
  trees at `3511677a`, `b64c2f8c`, `e299cd72`, `1e4e4b9e` and `8c3a13c4` and their parents.
- `tests/finite_boundary.py`, which is in the tree.
- No `tools/audit/round3..8` evidence file was opened. Commit stats listed one filename under
  `tools/audit/round5/`, and it is not cited.
