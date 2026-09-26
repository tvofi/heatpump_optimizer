# D3 verify-v1: catch-up unit (D3-s3-01..05), lens V1 (reproduce)

Environment: CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1, PYTHONPATH=tests/hastub. Evidence tree: detached worktree of origin/handoff/audit-r9-evidence at c71187a2a3b65cb50c940bf94bee1b38ed0cdb60, baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: 4 vCPU cloud container (box G1-V1), load1 0.08–3.28 across the runs, thread_factor 1.00 throughout.

Tally: 5 verify, 0 weaken, 0 refute, 0 unresolved.

tvofi's no-heavy-D3-rerun rule applied: no prescreen.py run, no mutant pool, no full-gate or quiet-window confirmation (quiet window not run, tvofi rule). The votes rest on the seat's recorded pre-screen evidence (prescreen.json, prescreen.jsonl, perturb_*.out) plus cheap targeted checks:
- (a) grep-confirmed each cited production line;
- (b) ran the seat's `distinguish.py`, an in-memory two-copy scenario harness, for all five mutants plus `--identity` (2.3–2.5 s each);
- (c) ran `probe.py M02 tests/open_meteo.py` with and without `--env TZ=Europe/Stockholm` (~1.5 s each).

`probe.py M19 tests/features.py --new '...'` (the seat's perturbation command) did not finish in 120 s, because features.py drives 3369 checks. It was killed as over the light-check budget. The four perturbations that drive features.py (M19, M20, M21, M24) are therefore cited from the seat's recorded perturb_*.out files, read verbatim.

## D3-s3-01 — open_meteo._parse_block naive-UTC guard deletable under the gate's UTC-only processes · VERIFY (medium)
- **Production line:** `open_meteo.py:209` is `if parsed.tzinfo is None:`.
- **distinguish.py:** `M02 [TZ=Europe/Stockholm] ... M02_differs=1`, baseline `2026-01-15T00:00:00+00:00` vs mutant `2026-01-14T23:00:00+00:00`. `--identity` under the same TZ: 0. `--tz=UTC`: 0. Both null controls reproduce.
- **probe.py:** no TZ gives `open_meteo_py_killed=0` (rc=0, failed=0). With `--env TZ=Europe/Stockholm`: `open_meteo_py_killed=1`, `failed=14`, with the same four named checks. This reproduces the recorded evidence exactly: 0 kills under the gate's own environment, 1 under a non-UTC process TZ.
- **Attacks:**
  - Contention: none; the box was near-idle, and the metric is a count.
  - Gate mode: the claim is precisely that the gate's process TZ is always UTC; the flip under a real `TZ=` reproduces.
  - Null control: reproduced.
  - Reach: real HA runs in the installation's own TZ, commonly not UTC.
  - Severity: medium is earned, since solar timestamps shift by the UTC offset.
- **Metric:** count of M02's 14 closure drivers going red under the gate's environment; separately, kills under TZ=Europe/Stockholm.

## D3-s3-02 — DrawStats.from_dict can zero a positive open-draw occurrence · VERIFY (medium)
- **Production line:** `dhw_draws.py:136` is `stats._open_kwh = max(0.0, float(data.get("open_kwh", 0.0)))`.
- **distinguish.py:** `M19 CLAMP_DROP`, baseline [1.5] vs mutant [0.0], differs=1: a shower in progress closes as 0.0 kWh instead of 1.5. `--identity`: 0.
- **Perturbation:** cited from the recorded `perturb_M19.out`: `features_py_killed=1`, failed=3, with two named checks. This matches the finding's observed value. It was not re-derived here.
- **Attacks:**
  - Gate mode: the full 16-driver closure ran at pre-screen.
  - Null control: reproduced.
  - Reach: `from_dict` runs on every store load in real HA, so a restart mid-shower is a real path.
  - Severity: medium is earned (real energy silently dropped).
- **Metric:** M19's closure drivers going red; distinguish.py's open_kwh after a store round trip.

## D3-s3-03 — MonthlyLedger.add's non-finite guard unpinned; NaN drops the month on reload · VERIFY (medium)
- **Production line:** `ledger.py:117` is `if not (np.isfinite(kwh) and np.isfinite(sek)):`, followed by `return`.
- **distinguish.py:** `M21 GUARD_OFF`, baseline [1, 1, {'kwh': 10.0, 'sek': 20.0}] vs mutant [1, 0, {'kwh': nan, 'sek': 21.0}], differs=1. `--identity`: 0.
- **Perturbation:** cited from the recorded `perturb_M21.out`: `finite_boundary_py_killed=1` (failed=1) and `features_py_killed=1` (failed=2), kills=2. This matches the finding.
- **Attacks:**
  - Gate mode: the 13-driver closure, including finite_boundary.py, already ran.
  - Unpinned side: finite_boundary.py corrupts stored leaves but never goes through the writer, and the guard sits on the write path, before `_month(...)["lines"]` is mutated.
  - Null control: reproduced.
  - Reach: the live store-write path.
  - Severity: medium (silent loss of a whole month on reload).
- **Metric:** M21's closure drivers going red; distinguish.py's month-survives-reload value.

## D3-s3-04 — No gate check observes a positive fold from DhwProfileLearner.async_fold_draw_stats · VERIFY (medium)
- **Production line:** `dhw_learning.py:379` is `if self._external_heat_active():`.
- **distinguish.py:** `M24 GUARD_OFF`, baseline 0.0 vs mutant 0.4396 kWh, differs=1. `--identity`: 0.
- **Perturbation:** cited from the recorded `perturb_M24.out`: `features_py_killed=0` for the seeded mutant. `perturb_M24_all.out` gives kills=0 for the stronger `if True:` mutant across features, finite_boundary, entities, plan_view, wood_advisor, guard_pins, manual_plan, config_flow_steps, solar_alignment and env_drift.
- **Attacks:**
  - Gate mode: the stronger mutant ran against 10 named drivers, so this is not a default-fixture artefact.
  - Null control: reproduced.
  - Reach: the live coordinator update path.
  - Severity: medium (silent learner degradation with no red check).
- **Metric:** distinguish.py's folded energy for an external-heat interval; closure kill counts on both mutants.

## D3-s3-05 — Disinfection write-failed notice memo unpinned (hygiene) · VERIFY (low)
- **Production line:** `legionella.py:453` is `if switch.failed == self.write_failed_notice:`.
- **distinguish.py:** `M20 GUARD_OFF`: five healthy cycles issue 5 registry deletes instead of 0, differs=1. `--identity`: 0.
- **Perturbation:** cited from the recorded `perturb_M20.out`: `features_py_killed=1`, failed=3, with two named checks. This matches the finding.
- **Attacks:**
  - Gate mode: the 14-driver closure already ran.
  - Null control: reproduced.
  - Reach: `LegionellaGuard._drive_switch` is on the live observe path.
  - Severity: low/hygiene is earned, since the repeated deletes are redundant but idempotent.
- **Metric:** registry-delete calls over 5 healthy observe cycles.
