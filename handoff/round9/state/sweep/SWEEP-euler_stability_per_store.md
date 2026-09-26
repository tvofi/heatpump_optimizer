# Sweep: "explicit-Euler stability judged per store instead of on the coupled step matrix"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Finding: D2-s1-01
(verified, medium). Not a ledger class (new).

## Enumerator (minimal, per the brief)

`grep -n "EULER_STABILITY_MAX_RATIO\|EULER_MONOTONE_MAX_RATIO" custom_components/heatpump_optimizer/thermal_model.py`
inside `ThermalModel._stability_substeps` (thermal_model.py:2419-2470),
widened to list every store the function bounds:

```
$ grep -n "EULER_STABILITY_MAX_RATIO\|EULER_MONOTONE_MAX_RATIO" custom_components/heatpump_optimizer/thermal_model.py
```

Reading `_stability_substeps`'s body (thermal_model.py:2419 onward) directly:
it computes one ratio per store (upper zone, lower zone when two-zone,
slab, DHW tank, buffer) each against its own diagonal bound
(`EULER_STABILITY_MAX_RATIO`, with the buffer alone judged against
`EULER_MONOTONE_MAX_RATIO` for the reason the function's own docstring
gives), then takes `n_sub` from the worst single store. No pairwise or
whole-matrix coupling term (e.g. the valve-throttled buffer<->zone
conductance the docstring itself describes) enters any bound.

## Positive control

Confirmed at thermal_model.py:2419-2450 (baseline `1936d5ca` and
`origin/main` — `thermal_model.py` is not in the 4-file diff, so both
match): the function's own docstring states the mechanism directly ("the
four boundary-floored masses are judged against
`EULER_STABILITY_MAX_RATIO`... the buffer is the exception"), and the
finder's number (35 L valved config: 43.47 K on a +1 kW bump vs 9.05e-2 K
on a +1e-3 kW bump) is the finding's own executed evidence, not re-run here
(a full solver timing/precision re-run is a heavier D2 measurement than
this sweep's minimal-enumerator budget covers for an N=1 class).

## Null control / widening

Every store `_stability_substeps` bounds (upper zone, lower zone, slab, DHW
tank, buffer) is judged the same single-store way; there is no second
mechanism in the function to widen to (no store is coupling-checked). So
the enumerator's widening returns exactly the set the finder already
described — no additional instance beyond the one finding.

## Perturbation

Not independently re-run (would require re-deriving the finder's own solver
harness under `tools/audit/round9/D2/s1/`); the finding already carries its
own perturbation in `m1_stability.py`.

## Disposition

| seam | disposition |
|---|---|
| thermal_model.py `_stability_substeps`, all five bounded stores judged on diagonal ratio only | instance — D2-s1-01 (one mechanism, one finding) |

## Count

N = 1 verified finding + 0 sweep-confirmed instances = **1**. **rca: false**,
matching the brief.

## Barrier proposal

None built (N < 3). The finder's own scope names the fix directly: judge
the coupled step matrix (or at minimum the valve-throttled buffer<->zone
pair) rather than each store's own diagonal — left for the fixer.

## Gate seconds

~0.01s (one grep, one manual read of a ~50-line function).
