# Round 9 sweep, thread S3 — class P1

**Property.** A non-finite (NaN/Inf) or malformed (wrong type, unbounded
magnitude, out-of-domain) value crosses a persisted-store boundary — a
`Store.async_load()` payload, or the equivalent snapshot round trip — with no
guard that catches it before it reaches production logic. Two seam shapes,
both widened from the class's 9 findings' `seam_rule`s across the whole
package:

- **NUMFIELD**: a numeric leaf a loader reads with `data.get(...)`/subscript
  and casts with `float()`/`int()`, with no `isfinite`/`isnan`/`isinf` (or
  equivalent domain) check anywhere in the same function before the value is
  stored or used. `int()` casts are excluded from this shape's `instance`
  disposition when wrapped in `try/except (..., ValueError, ...)`: CPython's
  `int()` already rejects NaN/Inf with `ValueError`, so those are `guarded`
  against non-finite (though not necessarily against unbounded magnitude,
  which stays `int` in Python with no overflow — see D1-s2-03).
- **DTNAIVE**: a `datetime.fromisoformat(...)` parse whose result is later
  combined with another `datetime` (subtraction/comparison) in the same
  function, where the enclosing `except` does not also catch `TypeError` (the
  offset-naive/offset-aware crash) and the value is not tz-normalised
  (`.replace(tzinfo=...)`/`.astimezone(`).

**Enumerator.** `enumerator.py` is a deterministic AST scan (no execution) of
every `from_dict`/`_load*`/`async_load*`/`apply_payload`/`_stored_peaks`/
`_load_switch_record` in `custom_components/heatpump_optimizer/*.py`.

    PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/P1/enumerator.py --list

**Positive control / probes.** `probes.py` re-finds every one of the 9
round-9 P1 findings, each as a runtime probe that imports the production
symbol and fails at baseline 1936d5ca (12 store-shape) plus 2 additional
sweep-found instances of the same mechanism (comfort_learning.py, not named
in any round-9 finding but the same NUMFIELD shape). All 14 probes still fail
unmodified on `origin/main` (db878b2) — none of the three merged PRs (#1641,
#1642, #1643) touch this class.

    PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/P1/probes.py

RESULT total_probes=14 count / RESULT failing_probes=14 count (both baseline
and origin/main).

**Null control.** `enumerator.py --fixture`: a clean loader with an
`isfinite` guard on its one numeric field scores `fixture_clean_unguarded=0`;
the same loader with the guard deleted (the one-line re-introduction) scores
`fixture_reintro_unguarded=1`. The enumerator moves under the perturbation.

**Ledger history.** `tools/audit/bugclasses.json`'s P1 entry lists 12 prior
instances across rounds 1–6 (same mechanism: `detector_idea` = "Enumerate
every Store/async_load and every float field its from_dict reads; fuzz each
with nan/inf/malformed strings across the whole store roster" — this is
exactly what `enumerator.py` + `probes.py` do). No pre-fix commit for those 12
was re-run (heavy history replay is out of scope for this cloud seat per the
no-heavy-D3-reruns rule, which this class is adjacent to but not itself; the
ledger's own ids are historical record, not re-derived here).

## Dispositions

| id | seam (file:line, function) | disposition | probe / note |
|---|---|---|---|
| D1-s1-01 | `snapshots.py` `SnapshotRing.due` — `(now - last)` outside its own `try` | **instance** | `probe_D1_s1_01_snapshots` |
| D1-s1-01 | `curve_learning.py` `CurveLearner._step_down` — `except ValueError` only, not `TypeError` | **instance** | `probe_D1_s1_01_curve_learning` |
| D1-s1-01 | `comfort_learning.py` `ComfortLearner._decay` — no `try` at all around `(now - self.last_update)` | **instance** | `probe_D1_s1_01_comfort_learning` |
| D1-s1-02 | `snapshots.py` `SnapshotRing.best_restore` — `np.isfinite(bias)` assumes `bias` is already numeric | **instance** | `probe_D1_s1_02_best_restore` (raises on a string `temperature_bias`) |
| D1-s2-03 | `coordinator.py` `_load_t4b_learners` — `int(entry[1])` has no magnitude bound | **instance** | `probe_D1_s2_03_sample_count` (loads `2**64`) |
| D1-s3-03 | `pump_arbiter.py` `_load` — `pair[0]` (the set-point) stored with zero type/finite check | **instance** | `probe_D1_s3_03_pump_arbiter` |
| D1-s3-06 | `freq_control.py` `FrequencyMap.from_dict` — `ratio` has a lower bound only (`ratio<=0`), `key`/decile has none | **instance** | `probe_D1_s3_06_freq_control` |
| D1-s4-01 | `defrost.py` `_grid_of("duty", float)` — no `isfinite` on cast cells | **instance** | `probe_D1_s4_01_defrost_duty` |
| D1-s4-03 | `defrost.py` `from_dict` — `duty`/`duty_counts` parsed all-or-nothing; one bad `duty_counts` cell discards a fully valid `duty` grid | **instance** | `probe_D1_s4_03_defrost_migration` |
| D1-s5-02 | `price_model.py` `PriceShapeModel.from_dict` — `residual_var` has no `isfinite` guard (unlike the sibling `shapes`/`quarter_factors` fields in the same function, which do) | **instance** | `probe_D1_s5_02_price_model_residual_var` |
| D1-s5-02 | `tariff.py` `PeakTracker.from_dict` — `_window_factor`/`_window_wsum` are `isfinite`-checked but not domain-bounded | **instance** | `probe_D1_s5_02_tariff_window_factor` |
| D14-s1-01 | `legionella.py` `async_load` — `attempt_peak` cast with `isinstance(peak,(int,float))` only, no `isfinite` | **instance** | `probe_D14_s1_01_legionella_attempt_peak` |
| — (new) | `comfort_learning.py` `from_dict` — `stored_configured = float(raw_configured)`, no `isfinite`; a NaN bypasses the `abs(...) > 1e-6` stale-weight gate (NaN comparisons are always `False`) rather than being discarded by it | **instance** | `probe_D14_s1_02_comfort_learning_gate_bypass` |
| — (new) | `comfort_learning.py` `from_dict` — `learned_weight`/`evidence` cast with `float()`, no `isfinite` | **instance** | `probe_D14_s1_03_comfort_learning_nonfinite_fields` |
| — | `price_model.py` `shapes`/`quarter_factors` (sibling fields of `residual_var`) | **guarded** | explicit `np.isfinite` check present, `#922` |
| — | `flow_lift.py` `FlowCurveBias.from_dict` `bias_k` | **guarded** | `bias` is `isfinite`-checked before the value that becomes `bias_k` is clamped from it |
| — | `dhw_draws.py` `DrawStats.from_dict` `_open_kwh`, per-event reservoir floats | **guarded** | explicit `isfinite`/`np.isfinite` checks present, `#1296` |
| — | `curve_learning.py` `bias` (the field itself, not `last_step_at`) | **guarded** | explicit `isfinite` check, `#1296` |
| — | `wear.py`, `curve_learning.py` `comfortable_days`/`resets`, `snapshots.py` `_bias_days`, `tariff.py` `_window_samples`, `dhw_learning.py` `cooling_samples`, `legionella.py` `_load_switch_record` `owned` | **not applicable** | `int()`-cast counters inside `try/except (..., ValueError, ...)`; NaN/Inf already raise `ValueError` inside `int()` itself, so no separate `isfinite` guard is needed for this shape |
| — | `accuracy.py` `AccuracySample.from_dict` `when` (`fromisoformat`) | **not applicable** | the parsed `when` is never combined with another datetime inside this function; any naive/aware mismatch is a defect of whichever caller later diffs it, out of this seam's scope — recorded as a **lead** below, not re-scanned here |
| — | `manual_plan.py` `ManualOverride.from_dict` `expires_at`/`created_at` | **guarded** | `expires_at` raises `ManualPlanError` deliberately (documented contract, not a silent crash); `created_at` catches `ValueError` and falls back to `None` |
| — | `ledger.py` `MonthlyLedger.from_dict` via `_clean_month` | **guarded** | quarantines malformed months individually (`dropped` counter), does not propagate a bad amount — this is I1's shape (guard exists, mutation-invisible), not P1's |

**Lead** (not measured here, per COMMON.md — outside this seat's scope):
wherever `AccuracySample.from_dict`'s `when` (and any other `fromisoformat`
result returned rather than combined locally) is later diffed against an
aware `now` by its caller, the same DTNAIVE mechanism can reappear one frame
away from the loader. The barrier proposal below already covers this by
construction (see "Barrier").

**Count.** N = 9 verified findings + 2 sweep-confirmed new instances (the
`comfort_learning.py` pair) = 11. The ledger's ≥3-instance threshold and the
class's `rca: true` (from CLASSES-DRAFT.json, already ≥3 before this sweep)
both hold; RCA stays owed.

**Barrier proposal.** A single validated-load helper,
`load_finite_field(data, key, default, *, cast=float, lo=None, hi=None)`,
used by every loader above in place of the current per-field
`float(data.get(...))`/`try/except` pairs: it converts, checks
`math.isfinite` for float casts, and clamps to `[lo, hi]` when given —
structurally unable to express "cast without a finiteness check" (the
CLAUDE.md rule-1 kind of fix: a structure that cannot express the defect,
not an enumerator promoted into a lint). Estimated cost: one new ~15-line
function in a shared module (`store_fields.py` or similar) plus one call-site
edit per seam above (~15 call sites); no new gate seconds beyond the
existing loaders' own test coverage. This is a proposal for the RCA/fix
seats, not built here (sweep threads do not fix, per this thread's brief).
