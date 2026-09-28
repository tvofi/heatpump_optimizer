# Sweep: "learned-correction clamp sized against an assumed range, not the model's curve"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Finding: D2-s2-02
(verified, medium). Not a ledger class (new).

## Enumerator

```
$ grep -n "FLOW_BIAS_CLAMP_K\|curve_supply_temp(\|emitter_design_delta_t" custom_components/heatpump_optimizer/*.py
```

widened to every hand-picked clamp constant in the learning modules:

```
$ grep -n "_CLAMP_K\|_CLAMP\b\|_CLAMP =" custom_components/heatpump_optimizer/flow_lift.py custom_components/heatpump_optimizer/curve_learning.py custom_components/heatpump_optimizer/comfort_learning.py
flow_lift.py:64:FLOW_BIAS_CLAMP_K = 15.0
flow_lift.py:179,221: np.clip(..., -FLOW_BIAS_CLAMP_K, FLOW_BIAS_CLAMP_K)

$ grep -rn "CLAMP\b" custom_components/heatpump_optimizer/*.py | grep -iE "clamp_k|clamp =|_clamp_c|_clamp_kw"
(no hits outside flow_lift.py)
```

`curve_learning.py` and `comfort_learning.py` have no comparably-shaped
fixed clamp constant on a learned correction; whatever bounds they apply
is either unbounded or already derived from configuration (not checked
further — out of the two named findings' scope, and no candidate turned
up to widen to).

## Positive control

`FLOW_BIAS_CLAMP_K = 15.0` (flow_lift.py:64), applied at both `np.clip`
call sites (:179, :221). The finding's own number: the model curve
(`curve_supply_temp`) tops out at 27.9 C for `emitter_design_delta_t`
configurations the flow allows, so a correction that can legitimately need
more than 15 K of bias is silently truncated, overstating COP by up to 37%.
Confirmed present at baseline `1936d5ca`; `flow_lift.py` and
`thermal_model.py` are unchanged on `origin/main` (neither in the 4-file
diff).

## Null control

No other clamp constant of this shape exists in the two other learner
modules checked (`curve_learning.py`, `comfort_learning.py`) — the widened
grep returns 0 additional candidates, so the enumerator does not
under-search the obvious neighbours.

## Perturbation

Not independently re-run (would require the finder's own thermal-model
harness under `tools/audit/round9/D2/s2/`); the finding already carries its
own executed perturbation and null control.

## Disposition

| seam | disposition |
|---|---|
| flow_lift.py:64,179,221 `FLOW_BIAS_CLAMP_K` vs `curve_supply_temp` | instance — D2-s2-02 |
| curve_learning.py, comfort_learning.py | not applicable — no comparably-shaped fixed clamp constant found |

## Count

N = 1 verified finding + 0 sweep-confirmed instances = **1**. **rca: false**,
matching the brief.

## Barrier proposal

None built (N < 3). The finder's own scope: derive the clamp from
`curve_supply_temp`'s actual range for the configured
`emitter_design_delta_t`, rather than a fixed 15 K — left for the fixer.

## Gate seconds

~0.01s (three grep invocations).
