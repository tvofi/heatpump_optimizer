# BLOCKED: body carries not landed on the roster

The re-cut body is ready (kept refused at refs/heads/handoff-wip/r10-replay-cost-budget-r2-body, 23cae49d).
`tools/pr/prepr.sh --body-check` and `carry_audit.py check` pass on it (7 of 7 routed to R10-REPLAY-COST-2).
`body_push.sh` refuses it: `carry_audit.py landed` reports `CARRY-LANDED: 7 missing`, because the
group R10-REPLAY-COST-2 is on origin/handoff/audit-r10-roster (wave-r10-groups.json line 17319) with an
empty `carry` list, and the seat may not edit the roster.

Question: who lands the 7 body carries (`carry_audit.py land-ops` printed no op for them) so that body_push can run?
No code was changed; the code head stays 130769e1db383e4c6e98b01c4a90b31173693cb7.
