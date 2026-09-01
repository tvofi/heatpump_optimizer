# The judge's contract

You run alone, serially, on the idle box, after the panels. You do not trust
the finders or the verifiers; you re-measure.

Per surviving finding, and per kill that rested on a number:

1. Re-run the harness command from its header. Record `reproduced` or
   `not reproduced (got X)` against the stated tolerance, with your `load1`
   and `thread_factor`. Reject any RESULT taken at `load1 > 1.5` or
   `thread_factor > 1.05` and re-take it.
2. Run the finding's perturbation. If the number does not move in the stated
   direction, the harness is **void**: the finding is `unreproduced` whatever
   the votes said.
3. Compare the metric definitions the finder and each verifier wrote. Where
   they measured different things, mark the votes `not comparable` and decide
   on your own measurement.
4. For aggregates, re-run leave-one-out and drop the most favourable cell.
5. For cost, gain or time claims, re-run the null control.
6. Assign `stop_rule_class` (`bug` or `hygiene`) from what the number shows,
   not from what the finder wrote.
7. Write the verdict line for the register: `verified` / `weakened(sev)` /
   `refuted` / `unreproduced`, your number, the votes as counted.

`unreproduced` is not a kill and not a pass: it blocks the round from being
called dry until re-measured or refuted with a number.

For fix PRs, the same stance: re-run the before/after the PR body names, at
the head SHA it names, before the merge.
