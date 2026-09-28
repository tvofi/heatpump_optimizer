**Source:** the P7 class RCA in [RCA-BULK-1.md](https://github.com/tvofi/heatpump_optimizer/blob/handoff/audit-r9-alt/handoff/round9/state/alt/rca/RCA-BULK-1.md) §1, conducted 2026-09-28 because register v2 found that P7 was barriered without an RCA. Measured at origin/main `3490cb16`. The mutants and outputs are in [rca/bulk1](https://github.com/tvofi/heatpump_optimizer/tree/handoff/audit-r9-alt/handoff/round9/state/alt/rca/bulk1).

## What

F1.1 (#1665, merged `2d71759e`) landed the P7 barrier: `tests/dst_checks.py`'s DST tracer replays a committed day shifted onto a spring, an autumn and a plain day. The register's barrier text says it "reaches every seam a replayed cycle executes". The RCA put each historical member's pre-fix shape back into main and ran main's check:

| member | mutant | its own pins | the tracer check |
|---|---|---|---|
| R2 D2-03 (#243) | `_utc_step_starts` walks wall time | 4 FAIL | **FAIL** (caught) |
| R3 D2-02 (#777) | `window_factors` walks from `slot0` in wall time | 2 FAIL | **ok: blind** (the capacity tariff is never configured in the replay) |
| R5 D1-08 (#1299) | `_plan_age_minutes` subtracts raw | 3 FAIL | **ok: blind** (it ran 144 times, and every true age was 0 s: its operands never straddle the fold) |
| null: main | none | 66/66 pass | ok |

**The barrier reaches 1 of the 3 historical members.** The other two are held only by their per-instance pins. It is blind in two ways its text does not name:
- seams reached only by configuration;
- seams that execute, but whose operands never straddle the transition.

The finder's harness had a tariff arm, and the landed tracer dropped it.

Still at main: 13 raw zoned-datetime sites. `services.py:873` and `manual_plan.py:288` make a 20 h manual override last 21 h across the autumn fold. That figure is arithmetic, not a runtime observation.

## Cost test

- 5 instances in 31 days (4.8 per month); mean span 24.7 h (n=4); up to 18 releases escaped per instance.
- Countermeasure: two replay arms, estimated ≤20 s per `dst_checks.py` run, about 2 h per month against about 119 h per month.
- **It passes.**

## Fix shape (R9-F10.1c, tests only)

- **Config arm:** the same three days with a capacity tariff and off-peak mask at 15 and 60 min, plus a manual plan applied before the fold.
- **Straddle arm:** the solve fails for 2 h across the transition, so stamps written before the fold are read after it.
- **Demonstration:**
  - The R3 and R5 mutants (`p7_mutants.py`) must now fail.
  - Main and the plain-day null stay green.
  - `services.py:873` and `manual_plan.py:288` are expected to fire. They get a fix or a named exemption: an owner-visible choice, since the override length is behaviour.
- Amend the P7 `barrier` text in the register to name what it does not reach. Register v2 already carries the gap in `barrier_gap`.

## Disposition

Scheduled: **R9-F10.1c**, after R9-F10.1b (the aware-default hastub clock).
