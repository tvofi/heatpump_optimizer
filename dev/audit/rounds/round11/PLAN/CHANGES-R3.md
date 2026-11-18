# Revision 3 against revision 2

Revision 2 is `819aa2e354`. Every hour is `tools/plan/replan.py`'s at the pin
in `PLAN.json`, run on the draft and on the unchanged roster blob of
`c7e683a6d4`; `PLAN.md`'s revision 3 section names the commands. A positive
hour is later.

| group, edge or move | before | after | objective term and rank reason | effect on in-flight work | hours |
|---|---|---|---|---|---|
| `PLAN.json` `objective` block | absent | baseline, pin, terms, 40 ranked groups, no edge, no disposition | all thirteen terms; `architect-planner.md` requires it | none | 0 |
| 13 open roster groups outside the seam plan | not in `PLAN.json` `groups` | listed, `origin: roster`, each ranked | `objective-check` refuses an open group with no rank | none: briefs, files and edges stay the roster's | 0 |
| triage rows D0-s3-01, D11-s1-01 to D11-s1-06, D11-s2-01, D11-s3-02 to D11-s3-04, D17-s1-01, D5-s8-07 | `defer` to round 12, no card | `defer` to round 12, `card: P11` | `escapes`, `lead_time`: a verified bug deferred with no card buys the round's lead time with its own | none started. D11-s1-06 owes the in-round overlay; D0-s3-01, D17-s1-01 and D11-s2-01 lead round-end triage | 0 |
| edge `R11-SEAM-dead-state` after `R11-SEAM-store` | no edge; `dead-state` took the coordinator turn first, by name | `store` first | `escapes` (five bug findings removed): rank 1 before rank 2 on the coordinator turn | neither is started, no design or fix ref for either. Dispatch `store` at the turn `dead-state` held | `store` -33.95; `dead-state` +33.95; closure 0 |
| edges `R11-SEAM-comments-production` after the ten predecessors of `R11-SEAM-product-text` | no edge; first wave | after the behaviour seams (ADR-010) | `coverage`, `unowned`, `escapes` and five more NO-READ terms: the slot goes to their builder, rank 1 by card `E11-N-INTAKE-BUILDER` | design and verdict exist (`design/R11-SEAM-comments-production`, its `design-verdict`); no fixer dispatched. Hold the dispatch; the design stays, anchors re-read at the later base | `comments-production` +127.77; closure 0 |
| `R11-INTAKE-R10-RESIDUE` | waited for a slot, 14.22 h | first wave | as the row above | `dispatch/fixer-r11-intake-r10-residue` exists and the roster reads `not-started`: keep it running, re-sync the stage | -14.22 |
| `R11-PRE-TOKEN-LEDGER`, `R11-CLOSEOUT-CLEANUP`, `R11-SEAM-comments-tests` | later slot | the slot `comments-production` freed, in turn | none: rank 2, a side effect | leave alone | -3.38, -2.23, -3.93 |
| `R11-SEAM-kernel-layering` (rank 2, started) | running | running | none: no rank-1 group waits on it, and it delays none | keep. Stopping frees no rank-1 hour and forfeits the work since dispatch; 18.1 h remain by the model. It carries the `klayer` move | 0 |
| `R11-SEAM-governance-text` (rank 2, started) | running | running | as above | keep. 21.5 h remain by the model | 0 |
| `R11-SEAM-ratchet-raise` (rank 2, started) | running | running | as above | keep. 14.2 h remain by the model; ADR-009's rows | 0 |
| `R11-SEAM-actuation-release`, `R11-SEAM-config`, `R11-SEAM-tests` (rank 1, first wave, not started) | first wave | first wave | `escapes`: 6, 3 and 1 bug findings | dispatch now; 105.3 h of rank-1 work. `actuation-release` and `config` have a design and no `design-verdict` ref; the `tests` design is in flight (`handoff-wip/design-R11-SEAM-tests`). The design review is the first step of each | 0 |
| coordinator turn order, not-started groups | by name within a tier | `cycle-solve`, `actuation-writes`, `cycle-reporting`, `entity-service`, `inputs-freshness`, `learners`, `store`, then `fabric-learner`, `dead-state`, `cycle-surface` | rank 1 before rank 2 | a rank-2 group takes no coordinator turn while a ready rank-1 group waits | in the rows above |
| 21 rank-2 groups, `examined_by` | no examination planned | a close pass of the named dimension over each merged diff | `unexamined` | new work before the closeout stamp: one finder pass in each of D2, D5, D6, D7, D11, D13, D16 and D17 | not priced: `replan.py` has no duration for a finder pass |
| the round's projection | `projection.py`: 175.63 h at cap 3 | `replan.py` at the pin: wall 202.27 h, critical path 139.68 h | `lead_time`, `closure_slip`: the check derives every hour from the two projections | none | not comparable: a different model, and the pin is not the fork |

Rank-1 work as a whole: the last rank-1 group finishes 34.0 h earlier, and the
sum of rank-1 finish times falls by 48.2 h. The round's closure does not move.

No decided open point of revision 2 is changed. The nine stand, pending owner
confirmation as before.

## The dS target after the changes

The score target is the floor, and revision 3 moves nothing in it: the moves
and their predictions are revision 2's, so the planned case reads +24.3811 and
the floor case +22.9801 against +22.7. The target is still not shown reachable
by this plan alone, for revision 2's reasons: without the circ term the planned
case reads +21.1938, and admissibility rests on ADR-007's unmeasured `F`. Main
at `8751943e17` reads dS +0.0430 WORSENS, `coord_footprint` -0.0063.

The floor costs the round 35.53 h of critical path and 38.75 h of wall
(projection A less B). It delays no rank-1 group by more than 0.2 h.
