# Class sweep — "production member reached by no production code"

Not in `tools/audit/bugclasses.json` (new class this round).

Round-9 findings: **D7-s3-01** (verified, low — static AST reachability from HA's own entry
points finds 9 dead class members; `DefrostDerate.samples` is kept alive in every name-based
static view by a field-name collision with `AccuracyTracker.samples`, and only the dynamic
sentinel — driving 6 scenarios / 12 update cycles and recording every attribute HA actually reads
— shows it dead too, for 10 total) and **D7-s3-72** (verified, low — `ThermalModel._step_*`
per-step scratch attributes that are written every step but never read by any consumer).

## Enumerator

`tools/audit/round9/D14/sweep/production-member-no-caller/enumerate.sh`: family A reuses the
finder's own static (`tools/audit/round9/D7/s3/reach.py --list`) and dynamic
(`tools/audit/round9/D7/s3/sentinel.py`) harnesses; family B reuses
`tools/audit/round9/D7/leads/l3_write_only_scratch.py`, which already generalises to "any
attribute with production writes and zero production reads" per its own docstring.

Positive control: family A's static list reproduces exactly the 9 members D7-s3-01 names; the
dynamic sentinel adds the 10th (`DefrostDerate.samples`), which is D7-s3-01's own point about the
class (name collision defeats static reachability, so the class needs both a static and a dynamic
enumerator).
Null control: `sentinel.py`'s `dead_members_called_from_production=0` on the same fixture that
finds `dead_member_production_calls_total=0` for the confirmed-dead set, and the "live" control
members (`mode`, `optimization_running`, `stale_keys`, …) all show nonzero calls — the harness
does not over-report.
Perturbation: `reach.py --perturb-live NAME` (append a live module-level load of `NAME`) drops
`dead_reachability_total` by exactly 1 per property perturbed — the judge's own perturbation for
this harness.

## Disposition

| seam | disposition | note |
|---|---|---|
| `coordinator.py:2422 current_action`, `:2543 floor_return_temp`, `:2414 last_optimization`, `:2418 next_optimization` (4 properties) | **instance** | D7-s3-01 family — static + dynamic dead. |
| `defrost.py:327 DefrostDerate.measured` | **instance** | D7-s3-01 family — static + dynamic dead. |
| `inputs.py:147 InputHealth.healthy` | **instance** | D7-s3-01 family — static + dynamic dead. |
| `open_meteo.py:108 IrradianceSeries.start`, `:273 OpenMeteoSolar.last_success` | **instance** | D7-s3-01 family — static + dynamic dead. |
| `optimizer.py:1484 _Horizon.weather` | **instance** | D7-s3-01 family — static + dynamic dead. |
| `defrost.py DefrostDerate.samples` | **instance** | D7-s3-01's own named case — invisible to the static reach scan (name-collision with `AccuracyTracker.samples`), caught only by `sentinel.py`. |
| `thermal_model.py ThermalModel._step_dhw_refused`, `_step_dhw_floor_injected`, `_step_dhw_draw_kw`, `_step_wood_refused` | **instance** | D7-s3-72 — `write_only=True`, zero `self_reads`/`consumer_reads`. |
| `thermal_model.py ThermalModel._step_buffer_refused` | **not applicable** | `write_only=False` — read by `ThermalModel.simulate_trajectory` (98,688 consumer reads in the fixture). |

## Count

N = 2 verified findings (D7-s3-01 covers all 10 family-A members as one finding; D7-s3-72 covers
the 4 family-B members as one finding) + 0 additional sweep-confirmed instances beyond what the
two findings already enumerate. **rca = false** (N=2 < 3, not a ledger class, not barriered).

## Barrier proposal

Fold `reach.py`'s static reachability scan plus a dynamic sentinel pass (a cheap smoke run of the
existing scenario fixture with attribute-read tracing) into `tests/structure.py`'s dead-code
metric, replacing its property-skipping method screen; add the write-only-scratch check
(`l3_write_only_scratch.py`'s generalised form) as a second structural metric. Estimated gate
cost: reach.py + sentinel.py + l3_write_only_scratch.py together run in a few seconds (no solver
loop, pure AST + one instrumented smoke pass).
