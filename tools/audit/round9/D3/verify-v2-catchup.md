# D3 verify-v2, extra unit "catchup" (D3-s3-01..05)

Lens V2 (independent), box G1-V2. Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`,
worktree at `c71187a2`. No mutation pre-screen, no mutant pool, no full gate
run, per tvofi's 2026-09-26T11:37Z rule: findings are voted on the seat's
recorded pre-screen evidence (`tools/audit/round9/D3/s3/pool.json`,
`prescreen.json`, `REPORT.md`), cited rather than re-executed. Step 1's
"re-run the harness" is the finder's own `distinguish.py`, a single
targeted per-mutant scenario check (~2.8s wall for all five mutants, no
suite import) -- allowed under the standing rule's "one fast script under
~2 minutes" exception, and is not the pre-screen. Step 2 is a harness I
wrote myself under `tools/audit/round9/D3/verify-v2/catchup_*.py`, each
building a second in-memory copy of the named production module with the
recorded mutant's `old`->`new` text substitution applied (never a
subprocess, never a suite script), then calling the production symbol
directly on both copies. All five anchors (file:line, `old` text) still
match the current tree exactly.

All five ran on an otherwise-idle seat: `load1` 0.43-1.22, `thread_factor`
1.00 throughout (no BLAS import on any of these five paths -- open_meteo's
math is stdlib `datetime`, dhw_draws/ledger's only numpy call is
`np.isfinite` on scalars, dhw_learning/legionella touch no numpy at all).
These are provisional in the sense that the box is shared, but they are
count/value comparisons, not timings, so contention cannot move them short
of the harness contract's 3600s-timeout case, which none hit (runtime
under 1s each).

## D3-s3-01 (M02, open_meteo.py:209, naive-stamp UTC guard)

- **Step 1 (re-run finder's `distinguish.py`)**: `M02_differs=1`
  (baseline first instant `2026-01-15T00:00:00+00:00` under
  `TZ=Europe/Stockholm`, mutant `2026-01-14T23:00:00+00:00`) -- reproduces
  the finder's number exactly.
- **Step 2 (own harness, `catchup_m02.py`)**: my own metric definition --
  among 5 fixture blocks built the same way `tests/open_meteo.py:block()`
  builds them (not the finder's own scenario), the count on which real vs.
  mutant `_parse_block` disagree on the first returned UTC instant.
  `differ_tz=5/5` under `TZ=Europe/Stockholm`; `differ_utc=0/5` under
  `TZ=UTC` (my own null control, independent of the finder's).
  `load1=1.22`, `thread_factor=1.00`.
- **Attacks**: not contention (count metric, ratio-immune); gate mode N/A
  (no golden/env_drift call on this path); not a grid artefact (single
  fixed scenario per side, both mine and the finder's); null control
  present and passing on both sides (differ=0 at the process's own zone);
  reachable in real Home Assistant -- a container set to the user's local
  zone is an ordinary HA deployment, not a `FakeHass`-only artifact;
  severity `medium` is earned -- every solar sample silently shifts by the
  UTC offset, a wrong-but-not-crashing published value.
- **Step 4 (test-gap mutation)**: the recorded mutant M02 itself
  (`open_meteo.py:209`, `if False:` for `if parsed.tzinfo is None:`) is the
  single-line production mutation; the file is
  `custom_components/heatpump_optimizer/open_meteo.py`.
- **Vote: verify**, severity medium.

## D3-s3-02 (M19, dhw_draws.py:136, DrawStats.from_dict open-occurrence clamp)

- **Step 1**: `M19_differs=1` (baseline `[1.5]`, mutant `[0.0]`, the
  finder's own fold-then-round-trip scenario).
- **Step 2 (own harness, `catchup_m19.py`)**: own metric -- direct
  `from_dict()` calls with `open_kwh` in `{0.0, 1.5, 1e9, -3.0, nan, inf}`.
  `differ=2/6`: only `1.5` and `1e9` (the positive-finite cases) differ
  (real keeps them, mutant zeroes them); `0.0`, `-3.0`, `nan`, `inf` already
  read `0.0` in production via the same `max(0.0, ...)`/`isfinite` clamp, so
  the mutant is indistinguishable there -- itself a null control on the
  clamp path. `load1=0.58`, `thread_factor=1.00`.
- **Attacks**: no contention issue (count/value metric); no gate-mode
  question; no grid aggregate; null control present (the 4/6 agreeing
  inputs); reachable in real HA -- `DrawStats.from_dict` runs on every
  store reload after a restart, not only inside the test stub; severity
  `medium` earned -- an in-progress shower's energy silently resets to 0 on
  a restart mid-shower, a real but bounded (single-occurrence) loss.
- **Step 4**: the recorded mutant M19 (`dhw_draws.py:136`,
  `stats._open_kwh = (0.0)` for `max(0.0, float(data.get("open_kwh", 0.0)))`)
  in `custom_components/heatpump_optimizer/dhw_draws.py`.
- **Vote: verify**, severity medium.

## D3-s3-03 (M21, ledger.py:117, MonthlyLedger.add non-finite guard)

- **Step 1**: `M21_differs=1` (baseline `[1, 1, {'kwh': 10.0, 'sek':
  20.0}]`, mutant `[1, 0, {'kwh': nan, 'sek': 21.0}]`).
- **Step 2 (own harness, `catchup_m21.py`)**: own scenario -- one finite
  `add()` (kwh=10.0) then one non-finite `add()` (kwh=nan) on the same
  month, then an `as_dict()`/`from_dict()` round trip. Real:
  `months_after=1`, `kwh_after=10.0` (the finite write survives, the NaN
  write is refused at the guard). Mutant: `months_after=0`,
  `kwh_after=None` (`_clean_month` drops the whole month because the
  unguarded NaN line reached disk). `differ_months_after_reload=1/1`.
  `load1=0.52`, `thread_factor=1.00`.
- **Attacks**: not contention; not gate-mode; not a grid artefact; null
  control is the real-side result itself (finite write alone would survive,
  and does); reachable in real HA -- `MonthlyLedger.add` is called on every
  settled tick, and a NaN amount is a real (if rare) upstream possibility
  the guard exists to catch, per the module's own R5-D1 comment; severity
  `medium` earned -- silent loss of an entire month's cost-ledger line, a
  wrong-money defect but bounded to the one month and recoverable by the
  next write.
- **Step 4**: the recorded mutant M21 (`ledger.py:117`, `if False:` for
  `if not (np.isfinite(kwh) and np.isfinite(sek)):`) in
  `custom_components/heatpump_optimizer/ledger.py`.
- **Vote: verify**, severity medium.

## D3-s3-04 (M24, dhw_learning.py:379, async_fold_draw_stats external-heat guard)

- **Step 1**: `M24_differs=1` (baseline `0.0`, mutant `0.4396`, the
  finder's own fixed scenario).
- **Step 2 (own harness, `catchup_m24.py`)**: own scenario, built through a
  real `HeatPumpOptimizerCoordinator`/`DhwProfileLearner` (FakeHass/FakeEntry
  per `tests/harness.py`, the README's reuse row), not the finder's minimal
  fixture. No-wood-burn arm (guard reads False on both sides):
  `real=0.81664`, `mutant=0.81664`, `differ_fold=0/1` -- agreement, as it
  must be when the guard is not the thing deciding anything. Wood-burn arm
  (`_external_heat_active` forced True): `real=0.0` (the real guard skips
  the fold), `mutant=0.81664` (the mutant folds it anyway),
  `differ_fold_woodburn=1/1`. Direction and mechanism match the finder's
  claim; the absolute folded value differs (0.81664 vs. the finder's
  0.4396) because my scenario used a different tank volume/temperature
  drop -- an own metric definition, not a repro of theirs, as the brief
  asks. `load1=0.64`, `thread_factor=1.00`.
- **Attacks**: not contention; not gate-mode; not a grid artefact; null
  control present and it is the no-wood-burn arm itself (0 differ);
  reachable in real HA -- `_external_heat_active()` reads a real sensor
  signal (an auxiliary/wood heat source), not a test-stub-only path;
  severity `medium` earned -- a wood-burn interval's non-DHW heat gets
  folded into the learned draw profile, biasing it upward, a wrong (if
  slow-forming) learned value rather than a crash.
- **Step 4**: for the SEEDED mutant, M24 itself (`dhw_learning.py:379`,
  `if False:` for `if self._external_heat_active():`); the finding's
  stronger claim (that no check anywhere observes a positive fold at all,
  so an `if True:` mutant that folds nothing also survives) rests on the
  finder's own recorded `perturb_M24_all.out` kill count against ten
  drivers (features/finite_boundary/entities/plan_view/wood_advisor/
  guard_pins/manual_plan/config_flow_steps/solar_alignment/env_drift, all
  `kills=0`), cited per the no-heavy-D3-re-runs rule rather than re-run.
  Both live in `custom_components/heatpump_optimizer/dhw_learning.py`.
- **Vote: verify**, severity medium.

## D3-s3-05 (M20, legionella.py:453, write-failed notice memo)

- **Step 1**: `M20_differs=1` (baseline `0`, mutant `5`, the finder's own
  five-cycle scenario).
- **Step 2 (own harness, `catchup_m20.py`)**: own scenario, built the same
  way `tests/guard_pins.py`'s `_ceiling_signature_change_reraises_notice`
  builds a `LegionellaGuard` (a real `DisinfectionSwitch`, no owned/failed
  switch), five `_drive_switch(False)` cycles, counting
  `ir.async_delete_issue`/`create_issue` calls naming
  `dhw_disinfection_write_failed`. `real_calls=0/5`, `mutant_calls=5/5`,
  `differ=1` -- matches the finder's own number exactly, from an
  independently built scenario. `load1=0.43`, `thread_factor=1.00`.
- **Attacks**: not contention; not gate-mode; not a grid artefact; null
  control is the real side itself (0 calls, matching the memo's intended
  behaviour); reachable in real HA -- `_drive_switch` runs on every
  coordinator cycle in observe mode, and `ir.async_delete_issue` on an
  issue that is not currently raised is a harmless no-op in real Home
  Assistant (idempotent), which is exactly why the finder's own
  `stop_rule_class` is `hygiene` and severity `low` rather than `medium`;
  I agree with that classification -- the consequence is five redundant
  registry calls per five cycles, not a wrong value or a wrong action.
- **Step 4**: the recorded mutant M20 (`legionella.py:453`, `if False:` for
  `if switch.failed == self.write_failed_notice:`) in
  `custom_components/heatpump_optimizer/legionella.py`.
- **Vote: verify**, severity low (matches the finder's).

## Summary

| id | step1 (finder's harness) | step2 (own harness) | vote | severity |
|---|---|---|---|---|
| D3-s3-01 | differs=1 | differ_tz=5/5, differ_utc=0/5 | verify | medium |
| D3-s3-02 | differs=1 | differ=2/6 (positive-finite only) | verify | medium |
| D3-s3-03 | differs=1 | differ_months_after_reload=1/1 | verify | medium |
| D3-s3-04 | differs=1 | differ_fold=0/1, differ_fold_woodburn=1/1 | verify | medium |
| D3-s3-05 | differs=1 | real=0/5, mutant=5/5, differ=1 | verify | low |

Nothing unresolved. No refutes: on every finding, my own independently-built
scenario (never the finder's fixture, never a subprocess/suite run) shows the
same direction of disagreement between real and the recorded mutant that the
finder reported, so two of the panel's three verifiers would need their own
executed numbers to disagree before any of these move off `verify`.
