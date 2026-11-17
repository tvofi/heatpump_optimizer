Question: body_push.sh exited 4 (REFUSED CARRY-LANDED) at code head 684f554faf338e82ef5ac7251533d4701383effe; the six carries below land on the round's roster, which this seat may not write. Will the relay fold them and re-run body_push.sh?

Code is at refs/heads/handoff/r11-outside-honest-dhw-runs (684f554faf, fast-forward from 36af54c383): origin/main 5e2ef89b4e merged in (65be05a2b1) and four of P2's mutants re-anchored (684f554faf). The refused body is kept at refs/heads/handoff-wip/r11-outside-honest-dhw-runs-body (919cc22bde). tools/pr/prepr.sh at this head: rc=0. body_push's merge predictor no longer refuses.

The two items formerly routed to R11-OUTSIDE-HONEST-STARTS-RUNS-P2 (7cacd91e, 2f90ae76) now route to R11-OUTSIDE-HONEST-STARTS-RUNS-P3; their text changed (P2 merged as #3693, so the four stale mutant entries are re-anchored in this pull request), so their item ids are now 72ce280b and be94cc35.

Not done: tests/mutation_table.py --pin-killed. fixer.md step 2 assigns --pin-killed to ci-autofix.md's mutation-autofix lane; the brief's instruction to run it here is recorded as pending owner confirmation. The 79 sites are each disposed under ## Unpinned sites (prepr: "disposes of all 79 site(s)").

body_push.sh output:

```
fill-red: `## Red checks` already names mutation; nothing written
figure_block: refreshed 1 block(s) at 684f554faf33
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R11-OUTSIDE-HONEST-DHW-RUNS at 684f554faf33, 3 live, 3 dispatched carries, 0 refused
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS-P3 body item 72ce280b: not in its brief or carries: '- R11-OUTSIDE-HONEST-STARTS-RUNS-P2 merged (pull request #3693) with `dev/audit/harnesses/r11_honest'
CARRY-MISSING R11-OUTSIDE-HONEST-DHW-RUNS body item b2ce461c: not in its brief or carries: "- The settle and the unengaged combi double heating are not built (the note's routing: a group of th"
CARRY-MISSING R11-OUTSIDE-HONEST-DHW-RUNS body item d364f59d: not in its brief or carries: "- The clamped tail, test 7's figures (`tail` arm): the start count of the combined draw is the same "
CARRY-MISSING R11-OUTSIDE-HONEST-METERED-FLOOR body item 7502c4d5: not in its brief or carries: "- On the fixed-speed install of `r11_honest_starts_runs.py` (floor 5.5 kW) the planner's run power, "
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS-P3 body item 2d9b0f43: not in its brief or carries: '- On the base and the head alike the two-descent solve scores above one of its arms alone on some da'
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS-P3 body item be94cc35: not in its brief or carries: "- `finding-propagation.md`: `unclear`: a dependency on a handed-off, unmerged predecessor (P2's muta"
CARRY-LANDED: 6 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-outside-honest-dhw-runs-body 919cc22bdea209db4ea98351bfb9a5cf4beb28fa
```
