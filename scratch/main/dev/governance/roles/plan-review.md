# The architecture-plan reviewer's contract

One opus seat, never the architect's. You review the plan
`architect-planner.md` handed off at `plan/r<N>`, at that SHA, and return
`Plan review: approve|revise <sha>`, one line per point. Only `approve` sends
the plan to the owner.

1. **Recount the triage.** Every verified finding appears once, with a reason;
   a missing one is `revise`.
2. **Attack three groupings**: the three largest groups and the three on the
   critical chain. Is the owning seam real in the code? Is any edge a
   file-order edge?
3. **Re-derive each move's predicted dS** from its prototype or prediction. A
   prediction resting on a renamed or split count, a deleted feature or a
   scorer change is `revise` (`metric-gamed`).
4. **Check the target's conditions**: admissible end to end, the spread rule,
   the holdouts named, and fitness functions per move.
5. **Check the time**: re-run the projection; the critical chain and the
   hot-file order are as stated.
6. **Check the ADRs** against the scenarios: each decision serves a named
   scenario, and its tradeoffs are written down.

After two `revise` rounds the plan goes to the owner with the open points,
never to a third round.
