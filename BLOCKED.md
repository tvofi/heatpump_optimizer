Question: none. body_push.sh exited 4 (REFUSED CARRY-LANDED): one Forward-carry item of the round-2 body routes to R10-SAV-VALUATION-RESIDUE and must land on the round roster, which this seat may not write. The relay folds the carry and re-runs body_push.sh.

Code: refs/heads/handoff/r10-advisor-steady-start at b9568f332e5136e7974e74cf3102bc1e41f022c9 (tools/pr/prepr.sh rc=0 at that head, body check included).
Body: refs/heads/handoff-wip/r10-advisor-steady-start-body at c3d7864b4bb5392b43f28baabcf413712f429190 (the refused body, kept by body_push.sh).

body_push.sh output:

    fill-red: `## Red checks` already names mutation; nothing written
    ref_privacy (body) ok: no host identity in the body
    review-packet handoff: R10-ADVISOR-STEADY-START at b9568f332e51, 8 live, 8 dispatched carries, 0 refused
    CARRY-MISSING R10-SAV-VALUATION-RESIDUE body item 55dd448f: not in its brief or carries: '- The thermostat reference does not hold its setpoint on a single-zone house behind a throttling val'
    CARRY-LANDED: 1 missing
    body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
    body_push: REFUSED CARRY-LANDED
    body_push: refused body kept at handoff-wip/r10-advisor-steady-start-body c3d7864b4bb5392b43f28baabcf413712f429190
