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
   holdouts, fitness functions; a plan stopping at the floor with a cheap move
   left over is `revise`.
5. **Check the time and the objective**: re-run `plan_audit.py
   objective-check` at the plan SHA; the critical chain and the hot-file order
   are as stated; attack three ranks and three keyed effects in the code, the
   rank-1 groups with most predicted dS per finding first; read the floor cost
   against step 4's cheap test.
6. **Check the ADRs**: each serves a named scenario, its tradeoffs written.

After two `revise` rounds the plan goes to the owner with the open points,
never a third round.
