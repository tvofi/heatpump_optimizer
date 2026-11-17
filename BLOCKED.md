Question: body_push.sh exited 4 (REFUSED CARRY-LANDED) at code head 36af54c383993b5d7bcdffe8b83e1e9ca76b17dc; the carries land on the round's roster, which this seat may not write. Will the relay fold them and re-run body_push.sh?

Code is at refs/heads/handoff/r11-outside-honest-dhw-runs (36af54c383). The refused body is kept at refs/heads/handoff-wip/r11-outside-honest-dhw-runs-body (b8ef24299e). tools/pr/prepr.sh at this head: rc=0.

body_push.sh output:

```
fill-red: `## Red checks` already names mutation; nothing written
figure_block: refreshed 1 block(s) at 36af54c38399
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R11-OUTSIDE-HONEST-DHW-RUNS at 36af54c38399, 3 live, 3 dispatched carries, 0 refused
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS-P2 body item 7cacd91e: not in its brief or carries: '- R11-OUTSIDE-HONEST-STARTS-RUNS-P2 (handed off at `dbc806ce5f`, not on main) adds `dev/audit/harnes'
CARRY-MISSING R11-OUTSIDE-HONEST-DHW-RUNS body item b2ce461c: not in its brief or carries: "- The settle and the unengaged combi double heating are not built (the note's routing: a group of th"
CARRY-MISSING R11-OUTSIDE-HONEST-DHW-RUNS body item d364f59d: not in its brief or carries: "- The clamped tail, test 7's figures (`tail` arm): the start count of the combined draw is the same "
CARRY-MISSING R11-OUTSIDE-HONEST-METERED-FLOOR body item 7502c4d5: not in its brief or carries: "- On the fixed-speed install of `r11_honest_starts_runs.py` (floor 5.5 kW) the planner's run power, "
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS-P3 body item 2d9b0f43: not in its brief or carries: '- On the base and the head alike the two-descent solve scores above one of its arms alone on some da'
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS-P2 body item 2f90ae76: not in its brief or carries: "- `finding-propagation.md`: `unclear`: a dependency on a handed-off, unmerged predecessor (P2's muta"
CARRY-LANDED: 6 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-outside-honest-dhw-runs-body b8ef24299ee3f1372372b88153772cd258afae30
```
