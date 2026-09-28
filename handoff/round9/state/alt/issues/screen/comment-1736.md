**Shape screen addendum to RCA-1736**, measured at origin/main `3490cb16`. The full verdicts are in [SCREEN-1736-SHAPES.md](https://github.com/tvofi/heatpump_optimizer/blob/handoff/audit-r9-alt/handoff/round9/state/alt/SCREEN-1736-SHAPES.md), and the probes and outputs are in [evidence/screen](https://github.com/tvofi/heatpump_optimizer/tree/handoff/audit-r9-alt/handoff/round9/state/alt/evidence/screen). Each lead was run as a probe arm against a null arm.

## New members of this class, outside the three hubs (filed)

- #1752: the boost overlay mutates `_current_action` in place. After a cancel, a `no_prices` or `solve_failed` cycle keeps actuating max power and displace for 90 min. First released in v6.4.0. Scheduled as R9-EG-B9.
- #1753: the price tile and fuse advisor borrow the what-if limiter and cache, and restore them unconditionally (the #1517 shape). R9-EG-B9.
- #1754: the "already in flight" guard drops the re-solve an input change asked for, and a manual plan swapped mid-solve inherits the old plan's releases. R9-EG-B10.
- #1755: the worker-fallback streak is shared across entries. It is a sibling of this class (shared state across a boundary), and its trigger is conditional. R9-EG-B10.

EG-B1's per-solve record does not reach these objects, so they are fixed on their own and **before** EG-B1 (plan principle 3).

## Blast radius of the three hubs that RCA-1736 §3 did not list (carried into R9-EG-B1's brief and acceptance harness)

| id | verdict | probe vs null | what EG-B1 must do |
|---|---|---|---|
| H1 | confirmed | A scheduled cycle landing inside a button- or service-started away solve publishes day 16.0 / night 16.0 / min 16.0 / DHW min 20.0, against the configured 21.0 / 19.5 / 19.0 / 45.0. Economy publishes min 17.5. Null (away off): the configured values. | `_thermal_view` and `_dhw_view` read configured values, never the per-solve record. The card's schedule editor pre-fills from these keys, so a Save could persist the setback into options. That JS path was read, not run; the acceptance harness drives it. |
| H2 | mechanism only | The band handed to the comfort learner is 3.5 (economy) or 0.5 (away), against a configured 2.0. No quiet period was counted in 36 cycles. | A decision item: judge the quiet period against the band the solve used, or the configured one. The economy band is defensible, so this is not a defect until an effect is shown. |
| H3 | partial | Learning reads the pooled profile (refuted). The `normalize_profile` fallback returns the per-solve blend (1.84 away from pooled), so a #42 rollback persists the blend. The published advisor's `heaviest_window_kwh` flips 4.65/4.97 depending on the last writer. | `dhw_hourly_draw_pattern` stops being written per solve. The blend lives in the record, and the fallback and advisor read the pooled profile. |
| H4 | confirmed | Comfort mode after a burn: the learner's freeze sees `external_heat_active` for 6 of 6 cycles, and draws are folded 0 of 6 times. Null (auto): one cycle of lag, then 5 of 6. | The DHW learner's freeze reads the live flag, not `_current_state`'s per-solve copy. |
| P12 | true by reading | The executor hand-off barrier (`tests/entities.py:20040-20170`) checks only the callable, never its arguments. | Once the solve hands over a frozen record, extend the barrier to refuse a live hub object as an argument. |

Not filed:
- **C3** (what-if side effects on published PV and price-known in comfort, boost and off). It is cosmetic and converges on the next solve.
- **The 17 benign sites**, listed with reasons in the screen doc.

Register v2 (`alt/register/`) records this class as `N-shared-config` with the RCA-1736 instances plus these screen members, under `non_round_instances`.
