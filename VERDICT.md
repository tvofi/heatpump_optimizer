Fix review: merge 68646456c774b1d0e58e6c79f6fd0a38281d334c

bus-nonce: c9cdd61a64ba8c50f284d4cb7a65bffe

Round 2 delta re-check of the carry-missing class only. No pull request yet, so no review packet and no CI. Code head unchanged (68646456c774b1d0e58e6c79f6fd0a38281d334c); the earlier code review, mutation proof and controls stand.

## Findings

- The two earlier findings (vacuous stale-plan null control wording; no committed finder's harness) were dismissed in round 1 and are unchanged. Carry: dismissed: settled in the first round, no production behaviour at stake

## Evidence

- RESULT carry: `carry_audit.py landed` against origin/handoff/audit-r10-roster (a6e03cd72a, contains 84184ae668) prints "CARRY-LANDED: 0 missing" (ev/carry-landed.txt).
- RESULT self-contained: the roster carry (ev/roster-carry-entry.txt) names pull request 3457, `cycle_supply`, both sites (`async_publish_current_action` displace/set-point; the legacy payload's `heat_pump_on`) and the control (cycle landing one step late vs switch write; null: same cycle inside its step). The old "sites above" wording is gone; the body (8293b160) names both sites inline and cites roster commit 84184ae668.
- RESULT body delta: only the three carry lines changed versus the prior body; all other claims unchanged.
- RESULT merge: git merge-tree --write-tree origin/main 68646456c774b1d0e58e6c79f6fd0a38281d334c rc=0, no conflict (ev/merge-tree.txt).
- Reds: no CI before the PR opens; not re-run.
