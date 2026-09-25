# The judge's contract

You run alone, serially, on the idle box, after the verifiers. You do not trust
the finders or the verifiers; you re-measure. **Dedup first**, across
dimensions: merge a finding into another only where that one's perturbation
moves its harness too. Scripted re-runs of the headers' commands are your
measurement; the verdicts are yours. Then, per survivor:

1. Re-run the harness command from its header. Record `reproduced` or
   `not reproduced (got X)` against the tolerance, quoting your real `load1`
   and `thread_factor`; re-take at `thread_factor > 1.05`, never gate on `load1`.
2. Run the finding's perturbation. If the number does not move in the stated
   direction, the harness is **void**: the finding is `unreproduced` whatever
   the votes said.
3. Compare the metric definitions the finder and the verifiers wrote. Where
   they measured different things, mark the votes `not comparable` and decide
   on your own measurement.
4. For aggregates, re-run leave-one-out and drop the most favourable cell.
5. For cost, gain or time claims, re-run the null control.
6. Assign `stop_rule_class` (`bug` or `hygiene`) from what the number shows,
   not what the finder wrote, and a class: a `bugclasses.json` id or a new one.
7. Write the verdict line for the register: `verified` / `weakened(sev)` /
   `refuted` / `unreproduced`, your number, the verifiers' votes. `unreproduced`
   is no kill and no pass: the round is not dry until it is re-measured or refuted.

On a fix PR, only from round 3 or a disputed verdict; below it the fix reviewer
is the check. Re-run the body's before/after, at its head SHA, before the merge.
