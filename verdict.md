Design review: approve 9aa450f55e0ddd261d48c41f9cc363027d52531f

Round 2 review of design/R10-DRAW-MAP-EVIDENCE at 9aa450f55e (the tip at start and at push). Scope: the delta from f334fc7d15 plus each round-1 point, read against origin/main 5b8f05ba4e merged with a827c3d985, the note's own base. The [CE] section is new, so it was read whole. Light checks only:
- the designer's budget168.py on the owner bundle (P7 reproduces: 4,751,393 non-replay bytes, 226 bytes short of the 24 h replay);
- sweep_comfort.py and sweep_yield.py, read rather than run;
- the accuracy-store save cadence: coordinator.py:6132, in the cycle step list, through `async_save_if_changed`;
- `DrawRange.ceiling_since` and its three consumers (draw_range.py:180 and :713, sysid.py:1332);
- the sysid view in the owner bundle, structure only.

## Round-1 points

1. Resolved. The schedule plus `relax_hours` is predicted at the band top and at the command, k is chosen from 5 down to 2, and the live abort stays the backstop (P8). One residue on the cooling side is carried as r12.
2. Resolved. The suspension is stated (`_planned_duty`'s experiment branch). A sweep-only stand-down for one pass applies under the pump's start temperature (`_dhw_start_below_c`, pump_arbiter.py:1803), and the fit and probe keep today's behaviour.
3. Resolved. There is one exclusion place on the predecessor's seam (`MeasuredCop.judge_floor`), using the existing literal, and the fit and probe change is disclosed with a reason. Its predicate is wider than that reason on heat-metered installs; carried as r13.
4. Resolved. Every addition is priced at indent 2 and 168 h (P7, reproduced), rows are stored as column strings with a cap of 672, and the drop order and its manifest list are stated.
5. Resolved. The bound is k × 0.5 h × band top, the metered energy is published, and the null is against the meter's integral. Price and hour are re-checked at each level boundary, and the start gate requires the remaining window and every in-span price under the cutoff.
6. Resolved. P9 overturned the round-1 hold. Set-points are now mapped once and held, low levels first, behind an 8 K band gate, and a yield report makes a collapsed sweep visible.
7. Resolved. `debug_replay.py` gains a trace input, with a null on the window the replay half also covers and a perturbed column.

## [CE] checks

- **Consistent with point 3.** A band-top sweep interval feeds the ceiling store, which is draw evidence, and is refused as efficiency evidence in `MeasuredCop`. These are different quantities, so there is no contradiction.
- **Consistent with the approved draw-floor design.** The capped floor and the evidence state read the window's run-asked pairs only, and no sweep interval enters the window or the idle readings. `draw_range.fold` stays the one routing place.
- **Write figure.** 672 rows × 79,006/1008 bytes = 52.7 KB, and the cycle-step save (coordinator.py:6132) runs 48 times a day. That gives about 2.5 MB/day, always on. The arithmetic and the cadence hold. It is about a third more than the store's current saves, and acceptable for an SD card if disclosed.

## Notes for the fixer

- **r12, comfort lower bound.** Under a held set-point a level whose inlet reaches the set-point stops the compressor (P9's held arm counts these minutes), so the least heat a level delivers is zero after that stop, not its commanded kW. Re-run P8's lower bound with zero heat after P9's predicted stop. If k changes, use it; if not, record the count. Carry: R10-DRAW-MAP-EVIDENCE (item r12)
- **r13, heat-metered installs.** `judge_floor` (accuracy.py:919 at a827c3d985) runs before the heat-meter branch of `_fold_measured_cop`. The stated reason ("drawn over asked is no efficiency reading") does not hold where heat is metered, because there the COP is heat over electrical. Either restrict the experiment refusal to installs with no heat meter, or state the reason that also covers metered installs (for example, part-load COP points biasing a scalar scale). Test the choice. Carry: R10-DRAW-MAP-EVIDENCE (item r13)
- **r14, `ceiling_since` consumers.** `DrawRange.ceiling_since` has three consumers: the probe's clock (sysid.py:1332), the lapse in `learned_max_kw` (draw_range.py:180), and `SolveBand.since_s` (:713). Give the probe clock a new probe-only reader and leave `ceiling_since` on all rows. Changed in place, it would leave a store holding only sweep samples with no "newest", so it would never learn a top, which defeats [CE] 1 and the decision's other arm. Test that 12 sweep-only samples learn a top whose lapse runs from the newest sample of either source, and that `_overdrawn` clears both sources alike. Carry: R10-DRAW-MAP-EVIDENCE (item r14)
- **r15, band collapse during settle.** The 8 K band gate is read at the start, but the set-points are mapped at the first step pass, one settle hour later, by which time the water may have warmed. Re-check the gate there and finish with "the water is too warm for a sweep". The remaining-window start gate needs a k before the comfort check picks one: gate on k = 2 at the start and re-check for the chosen k after the settle. Carry: R10-DRAW-MAP-EVIDENCE (item r15)
- **r16, held set-points.** Clear the five held set-points on `ArbiterState` on any action that is not a sweep, so a finished, aborted or stood-down sweep can never leave one in force. Carry: R10-DRAW-MAP-EVIDENCE (item r16)
- **r17, ceiling sample value.** The ceiling sample is the meter reading at the close of the interval, the probe's pairing. A sweep holds the top for one interval after a 0.25 level, so compare that reading with A's steady drawn mean for the same segment on the synthetic run, and state which value the store takes. Carry: R10-DRAW-MAP-EVIDENCE (item r17)
- **r18, gate on [CE] 2.** [CE] 2 (`armable` order) is built only on the owner's yes. Without one, today's order stands and B2 omits it. Carry: R10-DRAW-MAP-EVIDENCE (item r18)

## Decisions routed

- decision: owner. [CE] 2, the probe before the fit where the top is unlearned. Reviewer's view: yes on product grounds. The learned top sets every plan's booked electrical level, the fit only refines the house, and the cost is the fit's start delayed by about three 7-day probe clocks (`PROBE_DAYS_UNLEARNED`). The fact that must go with it: in the owner's bundle the experiment option is on, but `last_attempt` is null in the live view and in all 6 snapshots, and the phase is idle throughout. No arm was pressed during the collection, so the empty store is not something the arming order caused there. The sysid state is not persisted, so a press before the last restart would not show. Under either order the store fills only after a press.
- The flat-price and text-column decisions are unchanged from round 1 (both: yes).
