# Screen for RCA-1736 shapes: verdicts and blast radius

Measured at origin/main `3490cb16` (v6.7.10), 2026-09-28. RCA-1736 (#1736) named two shapes; this screen looked for
more of each.

1. **Code shape:** a long-lived shared object carries two meanings, its configured value and one operation's
   effective value. The operation writes into it in place, only one group gets an unwind, and readers are taught one
   at a time.
2. **Process shape:** a class recurs at 1–2 instances per round and never fires the per-round barrier trigger, and
   nothing folds a round into the register.

Three read-only screens found the leads:
- scoped writes (all 67 modules);
- aliasing and executor hand-offs;
- the register.

A probe seat then verified every code lead with a probe arm and a null-control arm. The probes and their outputs are
in `evidence/screen/`, and `VERDICTS.md` there has the full table. The process shape's results are in `register/` and
`rca/`.

## Code shape: verdicts

| id | object | verdict | blast radius | first release | disposition |
|---|---|---|---|---|---|
| S1 | `_current_action`, boost overlay in place (`boost.py:108`) | **confirmed** | After a cancel, the pump is actuated at max power and max displace for 90 min during a price outage or failed solve. Every `current_action` reader, plus the ledger and accuracy. | v6.4.0 | new issue, **R9-EG-B9** |
| S2 | `_simulation_cache` / `_last_simulation`, borrowed by the tile and fuse advisor, restored unconditionally | **confirmed** | A user what-if gets a spurious rate-limit or loses its answer, and the limiter is reset | v4.0.0 | new issue, **R9-EG-B9** |
| H1 | the hubs: a concurrent cycle inside the away/economy envelope publishes the setback | **confirmed** (day 16.0 vs 21.0; DHW min 20.0 vs 45.0) | `_thermal_view`/`_dhw_view` pre-fill the card's schedule editor, so a Save could persist the setback into options (the JS path was read, not run) | v2.8.0 | carry to **R9-EG-B1** (#1736) |
| H2 | the hubs: `_record_quiet_comfort_period` reads the effective band inside the envelope | **mechanism confirmed, no effect reproduced** (band 3.5/0.5 vs 2.0; 0 quiet periods counted in 36 cycles) | The persisted comfort weight, only in a flip range. The economy band is arguably the right yardstick. | v2.8.0 | carry to R9-EG-B1 as a decision item |
| H3 | the hubs: `dhw_hourly_draw_pattern` has two writers (the learner and the per-solve blend) | **partial**. Refuted: learning reads the pooled profile. Confirmed: the `normalize_profile` fallback returns the blend (1.84 off pooled), so a #42 rollback persists the blend. The advisor's `heaviest_window_kwh` flips 4.65/4.97 by last writer. | the persisted DHW profile (rare); the published advisor (every cycle) | v4.0.0 | carry to R9-EG-B1 |
| H4 | the hubs: `_current_state.external_heat_active` is copied only inside the solve and read at event time | **confirmed** (comfort: frozen 6/6 cycles, draws folded 0/6; auto: one-cycle lag) | DHW draw statistics stop learning for as long as the house is in comfort/boost/off; they feed the DHW advisor and the #20 heavy-day targets | v4.0.0 | carry to R9-EG-B1 |
| C1 | worker-fallback streak shared across entries | **confirmed, conditional** (A: 8 in-process solves vs 3 then capped) | two or more entries plus a per-entry job failure: the #783 cap never engages, and the repair flaps | v6.4.2 | new issue, **R9-EG-B10** |
| C2 | `_record_manual_release` writes into whichever override is current after the await | **confirmed** (O2 carries O1's 41 releases) | manual-plan attributes | v3.2.0 | new issue with C4, **R9-EG-B10** |
| C4 | the "already in flight" guard drops the re-solve an input change asked for (found by the C2 probe) | **confirmed** (no solve against O2) | A manual plan applied or cleared mid-solve is not actuated for up to one interval while its receipt says applied. H1 is the same guard's publishing side. | v3.2.0 | same issue as C2, **R9-EG-B10** |
| C3 | `_forecast_arrays` side effects from what-if calls | **partial, cosmetic.** Auto: overwritten by the next solve (refuted). Comfort/boost/off: `price_known_steps` and `pv` describe the what-if horizon. Snow: converges (refuted). | display only; nothing actuated or persisted | v2.8.0 | recorded here, **not filed** |
| P12 | the executor hand-off barrier (`tests/entities.py:20040-20170`) checks only the callable, never its arguments | **true by reading.** No live object is handed off unsnapshotted today; `_last_interval_record` is safe only by convention. | a future live-argument hand-off passes the barrier | — | carry to R9-EG-B1: its frozen per-solve record lets the barrier check arguments |

Benign after checking (17), with the reasons in the screens' reports:
- the other executor hand-offs, which pass snapshots;
- class and module state (no mutable defaults, and the `WeakKeyDictionary`s are keyed per entry);
- Store round-trips, which are sanitised or JSON-copied;
- learned-scale pushes, service writes and per-solve optimizer fields.

**Class membership.** S1, S2, H1–H4 and C2 are members of the #1736 class, `N-shared-config` in the v2 register. C4 is
its concurrency sibling. Register v2 lists them as `non_round_instances` of N-shared-config: they were found by a
screen, not an audit round.

## Process shape

See `register/REGISTER-V2.md`. In short, the register had not received a round-8 member (round 8 was never
classified) and had R9 members only on barriered classes. The R9 judge had also re-minted 20 of its 31 new classes that
already had ids, and split mechanisms below 3. Five classes (P4, P7, P8, P10, I2) never got an RCA, and N-structure-blind
reached the trigger only once its split was undone. The bulk RCAs in `rca/RCA-BULK-{1,2,3}.md` conduct every owed
RCA that was missing. `register/RCA-INVENTORY.md` records the 82 RCAs ever conducted, 40 of them previously
undocumented.
